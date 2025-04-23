import re
import pandas as pd
from scipy.stats import beta, entropy, pearsonr
from scipy.special import loggamma, digamma, gamma
import random
import numpy as np
from scipy.optimize import minimize
from metrics import *
import math
import argparse

def fit_beta_mode_concentration(mode, concentration):
    """
    Compute parameters from the mode and concentration following this parameterization:
    https://en.wikipedia.org/wiki/Beta_distribution#Mode_and_concentration
    """
    alpha = mode * (concentration-2) + 1
    beta = (1-mode) * (concentration-2) + 1
    return alpha, beta


def certainty_linking_function(x, certainty):
    return x[0] * (x[1] ** certainty)


def objective_function_exp_concentration_map(x, df, metric, first_order=False, obj="pearson"):
    def map_certainty_to_concentration_local(certainty):
        return certainty_linking_function(x, certainty)

    # for field in ["prior", "posterior"]:
    if not first_order:
        prior = df.apply(lambda z: fit_beta_mode_concentration(z[f"prior_sliderResponse"],
                                                                    map_certainty_to_concentration_local(z[f"prior_confidence"])), axis=1)
        posterior = df.apply(lambda z: fit_beta_mode_concentration(z[f"posterior_sliderResponse"],
                                                                    map_certainty_to_concentration_local(z[f"posterior_confidence"])), axis=1)
    else:
        prior = df[f"prior_sliderResponse"]
        posterior = df[f"posterior_sliderResponse"]


    r = [g(metric(pre, post), x[2]) for pre, post in zip(prior, posterior)]
    try:
        if obj == "pearson":
            to_return = -pearsonr(df["relevance_sliderResponse"], r)[0]
        elif obj == "mse":
            to_return = np.mean([(rel - score)**2 for rel, score in zip(df["relevance_sliderResponse"], r)])
        elif obj == "std":
            to_return = -np.std(r)
        elif obj == "centrality":
            to_return = (0.5 - np.mean(r))**2
        elif obj == "pearson_reg":
            p = 0.5
            to_return = p * -pearsonr(df["relevance_sliderResponse"], r)[0] + \
                        (1-p) * -np.std(r)
    except ValueError:
        to_return = np.inf
    return to_return

def objective_function_exp_concentration_map_all_metrics(x, df, first_order=False, return_metric_vals=False, return_judgments=False, obj="pearson"):
    def map_certainty_to_concentration_local(certainty):
        return certainty_linking_function(x, certainty)

    # for field in ["prior", "posterior"]:
    prior = df.apply(lambda z: fit_beta_mode_concentration(z[f"prior_sliderResponse"],
                                                                map_certainty_to_concentration_local(z[f"prior_confidence"])), axis=1)
    posterior = df.apply(lambda z: fit_beta_mode_concentration(z[f"posterior_sliderResponse"],
                                                                map_certainty_to_concentration_local(z[f"posterior_confidence"])), axis=1)
    if first_order:
        prior_fo = df[f"prior_sliderResponse"]
        posterior_fo = df[f"posterior_sliderResponse"]

    def compute_losses(metric, metric_is_first_order=False):
        if not metric_is_first_order:
            r = [g(all_metrics[metric](pre, post), x[2]) for pre, post in zip(prior, posterior)]
        else:
            r = [g(all_metrics[metric](pre, post), x[2]) for pre, post in zip(prior_fo, posterior_fo)]
        try:
            if obj == "pearson":
                to_return = -pearsonr(df["relevance_sliderResponse"], r)[0]
            elif obj == "mse":
                to_return = np.mean([(rel - score)**2 for rel, score in zip(df["relevance_sliderResponse"], r)])
            elif obj == "std":
                to_return = -np.std(r)
            elif obj == "centrality":
                to_return = (0.5 - np.mean(r))**2
            elif obj == "pearson_reg":
                p = 0.5
                to_return = p * -pearsonr(df["relevance_sliderResponse"], r)[0] + \
                            (1-p) * -np.std(r)
        except ValueError:
            to_return = np.inf
        return to_return, r

    rs = []
    judgments = []
    for metric in metrics_so:
        met, jud = compute_losses(metric)
        rs.append(met)
        judgments.append(jud)
    if first_order:
        for metric in metrics_fo:
            met, jud = compute_losses(metric, metric_is_first_order=True)
            rs.append(met)
            judgments.append(jud)

    to_return = [sum(rs)/len(rs)]
    if return_metric_vals:
        to_return.append(rs)
    if return_judgments:
        to_return.append(judgments)
    if not return_metric_vals and not return_judgments:
        return to_return[0]
    else:
        return tuple(to_return)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--training", help="Path to results file with `training data` for fitting beta parameters (this is probably round 1 data)")
    parser.add_argument("--input", help="Path to results file with actual official results")
    parser.add_argument("--output", default=None)
    parser.add_argument("--optimize_joint", default="separate", help="Whether to optimize each metric separately ('separate'), jointly ('joint'), or both ('both')")
    parser.add_argument("--first_order", action="store_true", help="Whether to include first order metrics.")
    parser.add_argument("--obj", default="pearson", help="Select the optimization objective. Options: pearson, mse, std, centrality, pearson_reg")
    args = parser.parse_args()

    df_train = pd.read_json(args.training, orient="records", lines=True)
    print(args.input)
    df = pd.read_json(args.input, orient="records", lines=True)
    metrics_so = {
        "beta_kl": lambda p, q: kl_dirichlet(q, p),
        "beta_entropy_change": entropy_reduction_dirichlet,
        "beta_bayes_factor_utility_1": beta_bayes_factor_util_1,
        "pure_second_order_belief_change": pure_second_order_belief_change,
    }
    metrics_fo = {
        "kl": lambda p, q: kl(q, p),
        "entropy_change": entropy_reduction,
    }
    all_metrics = metrics_so | metrics_fo
    
    A_INIT = 2
    B_INIT = 2
    G_INIT = 2
    # G_INIT = math.e
    
    A_BOUNDS = (1, np.inf)
    B_BOUNDS = (1, np.inf)
    G_BOUNDS = (1, np.inf)
    # G_BOUNDS = (math.e, math.e)


    # Do optimization for each metric separately, find optimal params x
    params = {}
    if args.optimize_joint in ["separate", "both"]:
        for metric in metrics_so:
            if args.optimize_joint not in ["separate", "both"]:
                continue
            print(metric)
            x = minimize(lambda x: objective_function_exp_concentration_map(x, df_train, metrics_so[metric], obj=args.obj),
                         # method='TNC',
                         method='SLSQP',
                         x0=np.array([A_INIT, B_INIT, G_INIT]),
                         bounds=[A_BOUNDS, B_BOUNDS, G_BOUNDS]
                         ).x
            params[metric] = x
            print(f"{x[0]} * {x[1]}^c")
            print(f"1-{x[2]}^-x")
            print(f"best loss: {objective_function_exp_concentration_map(x, df_train, metrics_so[metric], obj=args.obj)}")
            print()

    if args.first_order and args.optimize_joint in ["separate", "both"]:
        for metric in metrics_fo:
            print(metric)
            x = minimize(lambda x: objective_function_exp_concentration_map(x, df_train, metrics_fo[metric], obj=args.obj, first_order=True),
                         # method='TNC',
                         method='SLSQP',
                         x0=np.array([A_INIT, B_INIT, G_INIT])
,
                         bounds=[(2, 2), (2, 2), G_BOUNDS]
                         ).x
            params[metric] = x
            print(f"1-{x[2]}^-x")
            print(f"best loss: {objective_function_exp_concentration_map(x, df_train, metrics_fo[metric], first_order=args.first_order, obj=args.obj)}")
            print()

    if args.optimize_joint in ["joint", "both"]:
        print("Joint")
        x = minimize(lambda x: objective_function_exp_concentration_map_all_metrics(x, df_train, first_order=args.first_order, obj=args.obj),
                         # method='TNC',
                         method='SLSQP',
                         x0=np.array([A_INIT, B_INIT, G_INIT]),
                         bounds=[A_BOUNDS, B_BOUNDS, G_BOUNDS]
                     ).x
        params["joint"] = x
        print(f"{x[0]} * {x[1]}^c")
        print(f"1-{x[2]}^-x")
        vals = objective_function_exp_concentration_map_all_metrics(x, df_train, return_metric_vals=True, first_order=args.first_order, obj=args.obj)
        print(f"best avg correlation: {-1 * vals[0]}")
        print(f"per metric: {str({k:v for k,v in zip(metrics_so.keys(), vals[1])})}")


    # Actually compute the beta params for each item and each metric (unless we are running the grid search)
    if args.optimize_joint in ["separate", "joint", "both"]:
        results = []
        def compile_results(use_joint=False):
            for metric in params:
                metric_name = metric + "_joint" if use_joint else metric
                for p in ["prior", "posterior"]:
                    df[f"{p}_concentration"] = df[f"{p}_confidence"].apply(
                        lambda c: certainty_linking_function(params[metric], c))
                    df[f"{p}_beta_for_{metric}"] = df.apply(
                        lambda row: fit_beta_mode_concentration(row[f"{p}_sliderResponse"], row[f"{p}_concentration"]),
                        axis=1)
                    df.drop(f"{p}_concentration", axis=1, inplace=True)

                def objective(metric, obj):
                    x = params[metric] if not use_joint else params["joint"]
                    if metric == "joint":
                        return objective_function_exp_concentration_map_all_metrics(x, df_train, first_order=args.first_order, obj=obj)
                    else:
                        first_order = metric in metrics_fo
                        return objective_function_exp_concentration_map(x, df_train, all_metrics[metric], first_order=first_order, obj=obj)

                results.append({
                    "metric": metric_name,
                    "a_fit": params[metric][0] if not use_joint else params["joint"][0],
                    "b_fit": params[metric][1] if not use_joint else params["joint"][1],
                    "g_fit": params[metric][2] if not use_joint else params["joint"][2],
                    "pearson": objective(metric, obj="pearson"),
                    "mse": objective(metric, obj="mse"),
                    "std": objective(metric, obj="std"),
                    "centrality": objective(metric, obj="centrality"),
                    "pearson_reg": objective(metric, obj="pearson_reg"),
                })

        compile_results()
        if args.optimize_joint in ["both", "joint"]:
            compile_results(use_joint=True)

        results = pd.DataFrame(results)
        results.to_csv(f"{args.output}_params.csv")
        df.to_json(args.output, orient="records", lines=True)

    # Run a grid search and save heatmaps
    # if args.optimize_joint == "grid":
    #     # First run the grid search
    #     a = np.linspace(1.01, 5, 2)
    #     b = np.linspace(1.01, 5, 2)
    #     c = np.logspace(1, 100, num=2, base=1.1)
    #     # c = np.array([1.1, 1.3, 1.8, 2.5, 5, 10, 20, 50, 200, 1000, 5000, 10000])
    #     A, B, C = np.meshgrid(a, b, c, indexing='ij')  # shape will be (12, 12, 20)
    #     grid = np.stack([A, B, C], axis=-1).reshape(-1, 3)
    #     zeros = np.zeros_like(grid)
    #     rows = []
    #
    #     from tqdm import tqdm
    #     for x in tqdm(grid):
    #         vals = objective_function_exp_concentration_map_all_metrics(x, df_train, return_metric_vals=True, return_judgments=True, first_order=args.first_order, obj=args.obj)
    #         row = {
    #             "a": x[0],
    #             "b": x[1],
    #             "r": x[2],
    #             "avg": vals[0]
    #         }
    #         for i, metric in enumerate(all_metrics):
    #             row[metric] = vals[1][i]
    #             row["judgments"] = vals[2][i]
    #         rows.append(row)
    #     df_results = pd.DataFrame(rows)
    #     df_results = df_results.set_index(["a", "b", "r"])
    #     print(df.sort_values("avg"))
    # #
    # #     # Then make the heatmaps
    #     import seaborn as sns
    #     import matplotlib.pyplot as plt
    #     metrics = list(all_metrics.keys()) + ["avg"]
    #     fig, axs = plt.subplots(1, 5, figsize=(20, 3))
    #     for metric, ax in zip(metrics, axs):
    #         df_metric = df[[metric]].unstack().droplevel(0, axis=1)
    #         sns.heatmap(df_metric, vmin=-0.65, vmax=-0.3, fmt=".2f", ax=ax)
    #         ax.set_xticklabels([f"{float(item.get_text()):.2f}" for item in ax.get_xticklabels()])
    #         ax.set_yticklabels([f"{float(item.get_text()):.2f}" for item in ax.get_yticklabels()])
    #         ax.set_title(metric)
    # #
    #     plt.tight_layout()
    #     plt.savefig(args.output)

