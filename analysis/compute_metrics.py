import numpy as np
import pandas as pd
import argparse
from scipy.stats import entropy

# This script takes the output from make_results_df.py
# Reshape dataframe and compute metrics: KL Utility, ER, and Bayes Factor


def wrangle_data(df_long, aggregrate_participants=False, aggregate_group=False):
    # 'index' determines which columns define unique rows
    index=[
        'submission_id', 
        'group',  # 'helpful' or 'relevant'?
        'StimID', 
        'AnswerCertainty', 
        'AnswerPolarity', 
        'ContextType', 
    ]
    # Participants and groups can be averaged over by removing column names from 'index'
    # because non-unique rows are aggregated by default in pivot_table
    if aggregrate_participants:
        index.remove('submission_id')
    if aggregate_group:
        index.remove('group')
    # Pivot dataframe so that TaskType values (prior/posterior/helpfulness) become columns
    df_wide = df_long.pivot_table(
        index=index,
        columns='TaskType',
        values=[
            'sliderResponse', 
            'confidence'
            ],
    ).reset_index()
    # Collapse multi-indexing: (SliderResponse, prior) -> SliderResponse__prior
    df_wide.columns = [
        '_'.join(reversed(col)).strip().lstrip('_')
        for col in df_wide.columns.values
    ]
    return df_wide

def kl(p, q):
    """
    :param p: posterior
    :param q: prior
    :return:
    """
    return entropy([p, 1-p], [q, 1-q], base=2)

def exp10(x):
    return 1 - (10 ** (-1 * x))

def entropy_reduction(p, q):
    """
    :param p: prior
    :param q: posterior
    :return: Absolute value of entropy reduction
    """
    return abs(entropy([p, 1-p], base=2) - entropy([q, 1-q], base=2))

def bayes_factor(p, q):
    """
    :param p: posterior
    :param q: prior
    :return: absolute value of log of bayes factor
    """
    if p == 1 and q == 1 or p == 0 and q == 0:
        return 0
    else:
        return abs(np.log10((np.float64(p) / (1-p)) * (np.float64(1-q) / q)))


def exp_bayes_factor(p, q):
    """
    :param p: posterior
    :param q: prior
    :return: expontential transformation of absolute value of log of bayes factor
    TODO: Find simpler closed form
    """
    if p == 1 and q == 1 or p == 0 and q == 0:
        return 0
    else:
        return exp10(abs(np.log10((np.float64(p) / (1-p)) * (np.float64(1-q) / q))))


def posterior_distance(p):
    """
    :param p: posterior
    :return: How far on a scale of 0 to 1 is p from 0.5
    """
    return 2 * abs(0.5 - p)

def prior_posterior_distance(p, q):
    """
    :param p: prior
    :param q: posterior
    :return: Distance between p and q
    """
    return abs(p - q)



def compute_metrics(raw_data, prior_colname, posterior_colname):
    """
    I've set all metrics except kl and bayes_factor to lie between 0 and 1.
    :param raw_data:
    :param prior_colname:
    :param posterior_colname:
    :return:
    """
    items = raw_data
    items['kl'] = items.apply(lambda x: kl(x[posterior_colname], x[prior_colname]), axis=1)
    items['kl_util'] = items.apply(lambda x: exp10(kl(x[posterior_colname], x[prior_colname])), axis=1)
    items['entropy_reduction'] = items.apply(lambda x: entropy_reduction(x[prior_colname], x[posterior_colname]), axis=1)
    items['bayes_factor'] = items.apply(lambda x: bayes_factor(x[posterior_colname], x[prior_colname]), axis=1)
    items['exp_bayes_factor'] = items.apply(lambda x: exp_bayes_factor(x[posterior_colname], x[prior_colname]), axis=1)
    items['posterior_distance'] = items.apply(lambda x: posterior_distance(x[posterior_colname]), axis=1)
    items['prior_posterior_distance'] = items.apply(lambda x: prior_posterior_distance(x[posterior_colname], x[prior_colname]), axis=1)
    return items 
    
if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="Relative path to a magpie .csv file containing the raw responses from the participants")
    parser.add_argument("--output", help="Name of output file")
    args = parser.parse_args()
    # Read filtered data from csv
    df = pd.read_csv(args.input)
    # Widen dataframe
    df = wrangle_data(df)
    # Compute predictor metrics
    df = compute_metrics(df, prior_colname='prior_sliderResponse', posterior_colname='posterior_sliderResponse')
    # Get outfile
    df.to_csv(path_or_buf=args.output)