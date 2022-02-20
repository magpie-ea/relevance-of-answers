import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--results_file", default="../results/pilot/results_processed.csv")
    parser.add_argument("--output_path", default="plots/violin_plot", help="Where to save plots to")
    parser.add_argument("--output_format", default="png", help="'pdf', 'png'")
    args = parser.parse_args()

    df = pd.read_csv(args.results_file)

    # Make trellises of violin plots by condition for every measurement / metric
    for name in ["relevance_sliderResponse", "prior_sliderResponse", "posterior_sliderResponse"]:
        y_name = name
        x_name, col_name = ("ContextType", None) if name == "prior_sliderResponse" else ("AnswerCertainty", "ContextType")
        # if name == "kl_exp" or name == "entropy_reduction":
        #     plot_data = df[df.apply(lambda x: x["helpfulness_range"] < 0.75 and
        #                                       x["prior_range"] < 0.75 and
        #                                       x["posterior_range"] < 0.75, axis=1)]
        # else:
        #     plot_data = df
        aspect = 1 if name == "prior" else 0.8
        x_order = ["negative", "neutral", "positive"] if name == "prior_sliderResponse" else ["exhaustive", "high_certainty", "low_certainty", "non_answer"]
        row_name = "AnswerPolarity" if name == "posterior_sliderResponse" else None
        g = sns.catplot(data=df,
                        x=x_name, y=y_name, col=col_name, row=row_name,
                        kind="violin",
                        cut=0, scale="width",
                        col_order=["negative", "neutral", "positive"], order=x_order,
                        palette="mako",
                        height=3.5, aspect=aspect)
        g.set_xticklabels(rotation=30, ha="right")
        name = name.capitalize()
        g.set_ylabels(name)
        g.set_xlabels("Answer")
        g.fig.suptitle(f"{name} by Answer/Context Condition")
        g.fig.tight_layout()
        # filtered = "_filtered_by_range" if name == "kl_exp" or name == "entropy_reduction" else ""
        out_name = f"{args.output_path}_{name}.{args.output_format}"
        plt.savefig(out_name)




