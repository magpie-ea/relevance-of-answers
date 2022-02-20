import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
from scipy.stats import pearsonr



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--results_file", default="../results/pilot/results_processed.csv", help="Path to results .csv file")
    parser.add_argument("--output_path", default="plots/corr_plot.", help="Where to save plots to")
    parser.add_argument("--output_format", default="png", help="'pdf', 'png'")
    args = parser.parse_args()

    df = pd.read_csv(args.results_file)

    metrics = ["relevance_sliderResponse",
               # "kl",
               "kl_util",
               "entropy_reduction",
               # "bayes_factor",
               "exp_bayes_factor",
               "posterior_distance",
               "prior_posterior_distance",
               "AnswerCertainty"
               ]

    df = df[[m for m in metrics]]
    g = sns.pairplot(df, hue="AnswerCertainty")
    for ax in g.axes.flatten():
        ax.set_xlim(-0.05, 1.05)
        ax.set_ylim(-0.05, 1.05)

    # Annotate with pearson r
    for i, m1 in enumerate(metrics[:-1]):
        for j, m2 in enumerate(metrics[:-1]):
            if i > j:
                r, _ = pearsonr(df[m1], df[m2])
                ax = g.axes[i, j]
                ax.annotate(f'r = {r:.2f}', xy=(.1, .9), xycoords=ax.transAxes)


    out = args.output_path + args.output_format
    plt.savefig(out)
