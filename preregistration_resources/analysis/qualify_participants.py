import argparse
import pandas as pd
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("--raw_responses", help="Relative path to a magpie .csv file containing the raw responses from the participants")
parser.add_argument("--output", help="Name of output file")
parser.add_argument("--exclude_pilot", action="store_true", help="Does the data include pilot data? Some pre-processing is necessary to address inconsistencies.")
parser.add_argument("--exclude_round1", action="store_true", help="Does the data include round 1 data?")
args = parser.parse_args()

ATTENTION_PASS_THRESHOLD = 1
REASONING_PASS_THRESHOLD = 0.625



df = pd.read_csv(args.raw_responses)
if args.exclude_pilot:
    df = df[df.submission_id.apply(lambda x: x >= 3008)]  # Exclude responses from beta testers (i.e. authors & friends)
    df = df[df.submission_id.apply(lambda x: x not in [3008, 3009])]  # Exclude responses from pilot 0.1. The p_min/p_max for attention check were wrong
    df = df[df.submission_id.apply(lambda x: x not in [3031])]  # Exclude author test

if args.exclude_round1:
    df = df[df.submission_id.apply(lambda x: x >= 5000)]  # All results from round 1 have submission ID less than 5000. This also excludes pilot data

# Make percents into probabilities
df["sliderResponse"] = df["sliderResponse"]/100

metadata = {}

# Calculate average time
experiment_duration_median = df["experiment_duration"].median() / 60000
print(f"Median experiment duration: {round(experiment_duration_median)} minutes")
metadata["experiment_duration_median"] = experiment_duration_median

# Number of participants
n_participants = len(df.submission_id.unique())
print(f"Total number of participants: {n_participants}")
metadata["n_participants"] = n_participants

# Quality checks
df_qual = pd.DataFrame(index=df.submission_id.unique())
for trial_type, threshold in zip(["attention", "reasoning"], [ATTENTION_PASS_THRESHOLD, REASONING_PASS_THRESHOLD]):
    df_tmp = df[df["TrialType"] == trial_type][["submission_id",
                                                "p_min", "p_max", "sliderResponse",
                                                "certainty_max", "certainty_min", "confidence"]]
    df_tmp["correct_p"] = df_tmp.apply(lambda x: x["sliderResponse"] <= x["p_max"] and x["sliderResponse"] >= x["p_min"], axis=1)
    df_tmp["correct_c"] = df_tmp.apply(lambda x: x["confidence"] <= x["certainty_max"] and x["confidence"] >= x["certainty_min"], axis=1)
    df_tmp = df_tmp[["submission_id", "correct_p", "correct_c"]].set_index("submission_id").stack().droplevel(1)
    df_tmp = pd.DataFrame(df_tmp).pivot_table(index="submission_id", aggfunc=np.mean)
    df[f'{trial_type}_score'] = df["submission_id"].apply(lambda x: df_tmp.loc[x])

df.to_json(path_or_buf=args.output, orient="records", lines=True)
