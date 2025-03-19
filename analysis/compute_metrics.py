import numpy as np
import pandas as pd
import argparse
from scipy.stats import entropy
from metrics import *
from ast import literal_eval


# This script takes the output from widen_dataframe.py or fit_beta.py
# Reshape dataframe and compute metrics: KL Utility, ER, and Bayes Factor


def compute_metrics(raw_data, prior_colname, posterior_colname, joint="separate"):
    """
    :param raw_data:
    :param prior_colname:
    :param posterior_colname:
    :param joint: whether beta distributions were optimized 'separate' for each metric, 'joint', or 'both'
    :return:
    """
    items = raw_data
    items['first_order_belief_change'] = items.apply(lambda x: prior_posterior_distance(x[posterior_colname], x[prior_colname]), axis=1)
    items['second_order_belief_change'] = items.apply(lambda x: prior_posterior_distance(x['prior_confidence'], x['posterior_confidence']), axis=1)
    items['entropy_change'] = items.apply(lambda x: entropy_reduction(x[prior_colname], x[posterior_colname]), axis=1)
    items['kl_utility'] = items.apply(lambda x: kl_util(x[posterior_colname], x[prior_colname]), axis=1)
    items['kl'] = items.apply(lambda x: kl(x[posterior_colname], x[prior_colname]), axis=1)
    items['bayes_factor_utility'] = items.apply(lambda x: bf_utility_polar(x[posterior_colname], x[prior_colname]), axis=1)
    if joint in ["separate", "both"]:
        items['beta_kl_utility'] = items.apply(lambda x: kl_util_dirichlet(x['posterior_beta_for_kl'], x['prior_beta_for_kl']), axis=1)
        items['beta_kl'] = items.apply(lambda x: kl_dirichlet(x['posterior_beta_for_kl'], x['prior_beta_for_kl']), axis=1)
        items['beta_entropy_change'] = items.apply(lambda x: entropy_reduction_dirichlet(x['prior_beta_for_entropy'], x['posterior_beta_for_entropy']), axis=1)
        items['beta_bayes_factor_utility'] = items.apply(lambda x: beta_bayes_factor_util(x['prior_beta_for_bf'], x['posterior_beta_for_bf']), axis=1)
        items['beta_bayes_factor_utility_1'] = items.apply(lambda x: beta_bayes_factor_util_1(x['prior_beta_for_bf'], x['posterior_beta_for_bf']), axis=1)
        items['pure_second_order_belief_change'] = items.apply(lambda x: pure_second_order_belief_change(x['prior_beta_for_2nd_order_change'], x['posterior_beta_for_2nd_order_change']), axis=1)
    if joint in ["joint", "both"]:
        items['beta_kl_utility_joint'] = items.apply(lambda x: kl_util_dirichlet(x['posterior_beta_for_joint'], x['prior_beta_for_joint']), axis=1)
        items['beta_kl_joint'] = items.apply(lambda x: kl_dirichlet(x['posterior_beta_for_joint'], x['prior_beta_for_joint']), axis=1)
        items['beta_entropy_change_joint'] = items.apply(lambda x: entropy_reduction_dirichlet(x['prior_beta_for_joint'], x['posterior_beta_for_joint']), axis=1)
        items['beta_bayes_factor_utility_joint'] = items.apply(lambda x: beta_bayes_factor_util(x['prior_beta_for_joint'], x['posterior_beta_for_joint']), axis=1)
        items['beta_bayes_factor_utility_1_joint'] = items.apply(lambda x: beta_bayes_factor_util_1(x['prior_beta_for_joint'], x['posterior_beta_for_joint']), axis=1)
        items['pure_second_order_belief_change_joint'] = items.apply(lambda x: pure_second_order_belief_change(x['prior_beta_for_joint'], x['posterior_beta_for_joint']), axis=1)
    return items

def scale_metrics(df, df_train, joint="separate"):
    # Now versions scaled between [0,1] if scale=True
    metrics_to_scale = [
        'entropy_change',
        'kl',
        'beta_entropy_change',
        'beta_kl',
        'beta_bayes_factor_utility',
        'beta_bayes_factor_utility_1',
        'pure_second_order_belief_change'
    ]
    if joint in ["joint", "both"]:
        metrics_to_scale.extend([m + "_joint" for m in [
            'beta_entropy_change',
            'beta_kl',
            'beta_bayes_factor_utility',
            'beta_bayes_factor_utility_1',
            'pure_second_order_belief_change'
        ]])
    results = []
    for metric in metrics_to_scale:
        from scipy.stats import pearsonr
        import numpy as np
        from scipy.optimize import minimize

        def objective(b, df, metric, obj="pearson"):
            scores = df[metric].apply(lambda m: g(m, b=b[0]))
            try:
                if obj == "pearson":
                    to_return = -pearsonr(df["relevance_sliderResponse"], scores)[0]
                elif obj == "mse":
                    to_return = np.mean([(rel - score)**2 for rel, score in zip(df["relevance_sliderResponse"], scores)])
                elif obj == "std":
                    to_return = -np.std(scores)
                elif obj == "centrality":
                    to_return = (0.5 - np.mean(scores))**2
                elif obj == "pearson_reg":
                    p = 0.5
                    to_return = p * -pearsonr(df["relevance_sliderResponse"], scores)[0] + \
                                (1-p) * -np.std(scores)
            except ValueError:
                to_return = np.inf
            # print(x, to_return)
            return to_return

        x = minimize(lambda b: objective(b, df_train, metric, obj=args.obj),
                     method='SLSQP',
                     x0=np.array([2]),
                     bounds=[(1.01, np.inf)]
                     ).x[0]
        results.append({
            "metric": metric,
            "x": x,
            "pearson": objective([x], df_train, metric, obj="pearson"),
            "mse": objective([x], df_train, metric, obj="mse"),
            "std": objective([x], df_train, metric, obj="std"),
            "centrality": objective([x], df_train, metric, obj="centrality"),
            "pearson_reg": objective([x], df_train, metric, obj="pearson_reg"),
        })

        df[metric + '_scaled'] = df[metric].apply(lambda m: g(m, b=x))

    results = pd.DataFrame(results)
    results.to_csv(f"{args.output}_optimization_results_{args.obj}.csv")
    return df
    
if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="Relative path to a (widened) .jsonl file containing one set of participant-vignette responses per row")
    parser.add_argument("--train", help="Relative path to a .jsonl file for fitting the scaling function parameter")
    parser.add_argument("--output", help="Name of output file")
    parser.add_argument("--scale", action="store_true", help="Whether to scale all metrics to fall in [0,1].")
    parser.add_argument("--joint", default="separate", help="Whether beta params are optimized 'separate' for each metric, 'joint', or 'both'.")
    parser.add_argument("--obj", default="pearson", help="Select the optimization objective. Options: pearson, mse, std, centrality, pearson_reg")


    args = parser.parse_args()
    # Read filtered data from csv
    df = pd.read_json(args.input, orient="records", lines=True)
    # Compute predictor metrics
    df = compute_metrics(df, prior_colname='prior_sliderResponse', posterior_colname='posterior_sliderResponse', joint=args.joint)

    if args.scale:
        df_train = pd.read_json(args.train, orient="records", lines=True)
        df_train = compute_metrics(df_train, prior_colname='prior_sliderResponse', posterior_colname='posterior_sliderResponse', joint=args.joint)
        df = scale_metrics(df, df_train, joint=args.joint)

    # Get outfile
    df.to_json(args.output, orient="records", lines=True)