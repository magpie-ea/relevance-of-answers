import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
from scipy.stats import pearsonr



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--results_file", default="../results/round_1.0/results_processed.jsonl", help="Path to results .csv file")
    parser.add_argument("--output_path", default="plots/corr_plot.", help="Where to save plots to")
    parser.add_argument("--exclude_extremes", action="store_true", help="Exclude non-answers and exhaustive answers, if desired.")
    parser.add_argument("--only_relevance", action="store_true")
    parser.add_argument("--output_format", default="png", help="'pdf', 'png'")
    args = parser.parse_args()

    df = pd.read_json(args.results_file, lines=True, orient="records")
    if args.exclude_extremes:
        df = df[df["AnswerCertainty"].apply(lambda x: x in ["high_certainty", "low_certainty"])]

    metrics = ["relevance_sliderResponse",
               # "kl",
               "kl_util",
               "entropy_reduction",
               # "bayes_factor",
               "exp_bayes_factor",
               "posterior_distance",
               "prior_posterior_distance",
               "kl_util_beta",
               "entropy_reduction_beta",
               "AnswerCertainty",
               ]

    df = df[[m for m in metrics]]
    if args.only_relevance:
        g = sns.pairplot(df, kind="scatter", hue="AnswerCertainty", y_vars=['relevance_sliderResponse'],
                         plot_kws={'alpha':0.2}, palette="colorblind", hue_order=["non_answer", "low_certainty", "high_certainty", "exhaustive"], markers=['o', 'v', 'P', 's'])
    else:
        g = sns.pairplot(df, kind="scatter", hue="AnswerCertainty", plot_kws={'alpha':0.15})

    for ax in g.axes.flatten():

        ax.set_xlim(-0.05, 1.05)
        ax.set_ylim(-0.05, 1.05)

    # Annotate with pearson r
    if args.only_relevance:
        for i, m in enumerate(metrics[1:-1]):
            try:
                r, _ = pearsonr(df[m], df["relevance_sliderResponse"])
            except ValueError:
                pass
            ax = g.axes[0, i+1]
            ax.annotate(f'r = {r:.2f}', xy=(.1, .9), xycoords=ax.transAxes)
    else:
        for i, m1 in enumerate(metrics[:-1]):
            for j, m2 in enumerate(metrics[:-1]):
                if i > j:
                    r, _ = pearsonr(df[m1], df[m2])
                    ax = g.axes[i, j]
                    ax.annotate(f'r = {r:.2f}', xy=(.1, .9), xycoords=ax.transAxes)


    out = args.output_path + args.output_format
    plt.savefig(out)
