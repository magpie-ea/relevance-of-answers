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


def objective_function_exp_concentration_map(x, df, metric, obj="pearson"):
    def map_certainty_to_concentration_local(certainty):
        return certainty_linking_function(x, certainty)

    # for field in ["prior", "posterior"]:
    prior = df.apply(lambda z: fit_beta_mode_concentration(z[f"prior_sliderResponse"],
                                                                map_certainty_to_concentration_local(z[f"prior_confidence"])), axis=1)
    posterior = df.apply(lambda z: fit_beta_mode_concentration(z[f"posterior_sliderResponse"],
                                                                map_certainty_to_concentration_local(z[f"posterior_confidence"])), axis=1)

    r = [metric(pre, post) for pre, post in zip(prior, posterior)]
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
    # print(x, to_return)
    return to_return

def objective_function_exp_concentration_map_all_metrics(x, df, metrics, return_metric_vals=False, obj="pearson"):
    def map_certainty_to_concentration_local(certainty):
        return certainty_linking_function(x, certainty)

    # for field in ["prior", "posterior"]:
    prior = df.apply(lambda z: fit_beta_mode_concentration(z[f"prior_sliderResponse"],
                                                                map_certainty_to_concentration_local(z[f"prior_confidence"])), axis=1)
    posterior = df.apply(lambda z: fit_beta_mode_concentration(z[f"posterior_sliderResponse"],
                                                                map_certainty_to_concentration_local(z[f"posterior_confidence"])), axis=1)
    rs = []
    for metric in metrics:
        r = [metrics[metric](pre, post) for pre, post in zip(prior, posterior)]
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
        rs.append(to_return)
    if return_metric_vals:
        return sum(rs)/len(rs), rs
    else:
        return sum(rs)/len(rs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--training", help="Path to results file with `training data` for fitting beta parameters (this is probably round 1 data)")
    parser.add_argument("--input", help="Path to results file with actual official results")
    parser.add_argument("--output", default=None)
    parser.add_argument("--optimize_joint", default="separate", help="Whether to optimize each metric separately ('separate'), jointly ('joint'), or both ('both')")
    parser.add_argument("--obj", default="pearson", help="Select the optimization objective. Options: pearson, mse, std, centrality, pearson_reg")
    args = parser.parse_args()

    df_train = pd.read_json(args.training, orient="records", lines=True)
    print(args.input)
    df = pd.read_json(args.input, orient="records", lines=True)
    metrics = {
        "kl_util": lambda p, q: kl_util_dirichlet(q, p),
        "kl": lambda p, q: kl_dirichlet(q, p),
        "entropy": entropy_reduction_dirichlet,
        "bf": beta_bayes_factor_util,
        "2nd_order_change": pure_second_order_belief_change
    }

    # Do optimization for each metric separately, find optimal params x
    params = {}
    if args.optimize_joint in ["separate", "both"]:
        for metric in metrics:
            if args.optimize_joint not in ["separate", "both"]:
                continue
            print(metric)
            x = minimize(lambda x: objective_function_exp_concentration_map(x, df_train, metrics[metric], obj=args.obj),
                         method='SLSQP',
                         x0=np.array([1, 2]),
                         bounds=[(0, np.inf), (1, np.inf)]
                         ).x
            params[metric] = x
            print(f"{x[0]} * {x[1]}^c")
            print(f"best loss: {objective_function_exp_concentration_map(x, df_train, metrics[metric], obj=args.obj)}")
            print()

    if args.optimize_joint in ["joint", "both"]:
        print("Joint")
        x = minimize(lambda x: objective_function_exp_concentration_map_all_metrics(x, df_train, metrics, obj=args.obj),
                     method='SLSQP',
                     x0=np.array([1,2]),
                     bounds=[(0, np.inf), (1, np.inf)]
                     ).x
        params["joint"] = x
        print(f"{x[0]} * {x[1]}^c")
        vals = objective_function_exp_concentration_map_all_metrics(x, df_train, metrics, return_metric_vals=True, obj=args.obj)
        print(f"best avg correlation: {-1 * vals[0]}")
        print(f"per metric: {str({k:v for k,v in zip(metrics.keys(), vals)})}")

    # Actually compute the beta params for each item and each metric (unless we are running the grid search)
    if args.optimize_joint in ["separate", "joint", "both"]:
        results = []
        for metric in params:
            for p in ["prior", "posterior"]:
                df[f"{p}_concentration"] = df[f"{p}_confidence"].apply(lambda c: certainty_linking_function(params[metric], c))
                df[f"{p}_beta_for_{metric}"] = df.apply(lambda row: fit_beta_mode_concentration(row[f"{p}_sliderResponse"], row[f"{p}_concentration"]), axis=1)
                df = df.drop(f"{p}_concentration", axis=1)

            def objective(metric, obj):
                if metric == "joint":
                    return objective_function_exp_concentration_map_all_metrics(x, df_train, metrics, obj=obj)
                else:
                    return objective_function_exp_concentration_map(x, df_train, metrics[metric], obj=obj)
            results.append({
                "metric": metric,
                "x": params[metric],
                "pearson": objective(metric, obj="pearson"),
                "mse": objective(metric, obj="mse"),
                "std": objective(metric, obj="std"),
                "centrality": objective(metric, obj="centrality"),
                "pearson_reg": objective(metric, obj="pearson_reg"),
            })

        results = pd.DataFrame(results)
        results.to_csv(args.output + "_optimization_results.csv")
        df.to_json(args.output, orient="records", lines=True)

    # Run a grid search and save heatmaps
    if args.optimize_joint == "grid":
        # First run the grid search
        values = np.linspace(1.01, 5, 12)
        X, Y = np.meshgrid(values, values)
        coordinates_np = np.dstack((X, Y))
        # zeros = np.zeros_like(coordinates_np)
        rows = []
        for i, _ in enumerate(coordinates_np):
            for j, x in enumerate(coordinates_np[i]):
                vals = objective_function_exp_concentration_map_all_metrics(x, df_train, metrics, return_metric_vals=True, obj=args.obj)
                row = {
                    "a": x[0],
                    "b": x[1],
                    "avg": vals[0]
                }
                for i, metric in enumerate(metrics):
                    row[metric] = vals[1][i]
                rows.append(row)
        df = pd.DataFrame(rows)
        df = df.set_index(["a", "b"])
        print(df.sort_values("avg"))

        # Then make the heatmaps
        import seaborn as sns
        import matplotlib.pyplot as plt
        metrics = list(metrics.keys()) + ["avg"]
        fig, axs = plt.subplots(1, 5, figsize=(20, 3))
        for metric, ax in zip(metrics, axs):
            df_metric = df[[metric]].unstack().droplevel(0, axis=1)
            sns.heatmap(df_metric, vmin=-0.65, vmax=-0.3, fmt=".2f", ax=ax)
            ax.set_xticklabels([f"{float(item.get_text()):.2f}" for item in ax.get_xticklabels()])
            ax.set_yticklabels([f"{float(item.get_text()):.2f}" for item in ax.get_yticklabels()])
            ax.set_title(metric)

        plt.tight_layout()
        plt.savefig(args.output)

