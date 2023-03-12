import numpy as np
import pandas as pd
import argparse


def wrangle_data(df_long, aggregrate_participants=False, aggregate_group=False):
    # 'index' determines which columns define unique rows
    index = [
        'submission_id',
        'group',  # 'helpful' or 'relevant'?
        'StimID',
        'AnswerCertainty',
        'AnswerPolarity',
        'ContextType',
        'attention_score',
        'reasoning_score'
    ]
    # Participants and groups can be averaged over by removing column names from 'index'
    # because non-unique rows are aggregated by default in pivot_table
    if aggregrate_participants:
        index.remove('submission_id')
    if aggregate_group:
        index.remove('group')
    # Pivot dataframe so that TaskType values (prior/posterior/helpfulness) become columns
    df_long["AnswerPolarity"] = df_long["AnswerPolarity"].fillna('dummy')
    df_wide = df_long.pivot_table(index=index, columns='TaskType',
                                  values=['sliderResponse', 'confidence']
                                  ).reset_index().replace('dummy', np.nan)
    # Collapse multi-indexing: (SliderResponse, prior) -> SliderResponse__prior
    df_wide.columns = [
        '_'.join(reversed(col)).strip().lstrip('_')
        for col in df_wide.columns.values
    ]
    return df_wide


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",
                        help="Relative path to a magpie .csv file containing the raw responses from the participants")
    parser.add_argument("--output", default=None, help="Name of output file")
    args = parser.parse_args()
    # Read filtered data from csv
    df = pd.read_json(args.input, orient="records", lines=True)
    # Widen dataframe
    df = wrangle_data(df)
    # Get outfile
    output = args.output if args.output else args.input
    df.to_json(output, orient="records", lines=True)
