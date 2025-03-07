import pandas as pd
import argparse




if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",
                        help="Relative path to a .json file containing the (partly) preprocessed data with all beta-values and metrics computed, and participant quality checks")
    parser.add_argument("--output", default=None, help="Name of output file")
    args = parser.parse_args()

    # Read filtered data from csv
    df = pd.read_json(args.input, orient="records", lines=True)

    # Widen dataframe
    for column_name in df.columns:
        if "beta_for" in column_name:
            df[f"{column_name}_a"] = df[column_name].apply(lambda x: x[0])
            df[f"{column_name}_b"] = df[column_name].apply(lambda x: x[1])
            df = df.drop(columns=[column_name])

    # Get outfile
    output = args.output if args.output else args.input
    df.to_csv(output)
