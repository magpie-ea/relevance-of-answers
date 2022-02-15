import argparse
import pandas as pd
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("--raw_responses", help="Relative path to a magpie .csv file containing the raw responses from the participants")
parser.add_argument("--output", help="Name of output file")
parser.add_argument("--pilot", action="store_true", help="Does the data include pilot data? Some pre-processing is necessary to address inconsistencies.")
args = parser.parse_args()

PASS_THRESHOLD = 0.75



df = pd.read_csv(args.raw_responses)
if args.pilot:
    df = df[df.submission_id.apply(lambda x: x >= 3008)]  # Exclude responses from beta testers (i.e. authors & friends)
    df = df[df.submission_id.apply(lambda x: x not in [3008, 3009])]  # Exclude responses from pilot 0.1. The p_min/p_max for attention check were wrong

# Make percents into probabilities
df["sliderResponse"] = df["sliderResponse"]/100

metadata = {}

# Calculate average time
experiment_duration_mean = df["experiment_duration"].mean() / 60000
print(f"Average experiment duration: {round(experiment_duration_mean)} minutes")
metadata["experiment_duration_mean"] = experiment_duration_mean

# Number of participants
n_participants = len(df.submission_id.unique())
print(f"Total number of participants: {n_participants}")
metadata["n_participants"] = n_participants

# Quality checks
df_qual = pd.DataFrame(index=df.submission_id.unique())
for trial_type in ["attention", "reasoning"]:
    df_tmp = df[df["TrialType"] == trial_type][["submission_id",
                                                "p_min", "p_max", "sliderResponse",
                                                "certainty_max", "certainty_min", "confidence"]]
    df_tmp["correct_p"] = df_tmp.apply(lambda x: x["sliderResponse"] <= x["p_max"] and x["sliderResponse"] >= x["p_min"], axis=1)
    df_tmp["correct_c"] = df_tmp.apply(lambda x: x["confidence"] <= x["certainty_max"] and x["confidence"] >= x["certainty_min"], axis=1)
    df_tmp = df_tmp[["submission_id", "correct_p", "correct_c"]].set_index("submission_id").stack().droplevel(1)
    df_tmp = pd.DataFrame(df_tmp).pivot_table(index="submission_id", aggfunc=np.mean)
    print(f"{trial_type} scores:")
    print(df_tmp[0].value_counts())
    print()
    df_qual = df_qual.assign(**{trial_type: df_tmp[0].apply(lambda x: x >= PASS_THRESHOLD)})
df_qual["pass"] = df_qual.apply(lambda submission_id: submission_id["attention"] and submission_id["reasoning"], axis=1)    # Define some passing criterion: Right now, it's just both attention and reasoning criteria were passed independently
df = df.join(df_qual[["pass"]], on="submission_id")

# Reduce results to all who passed, and to only experimental trials
df = df[df.apply(lambda x: x["TrialType"] == "main" and x["pass"], axis=1)]
df.to_csv(path_or_buf=args.output)