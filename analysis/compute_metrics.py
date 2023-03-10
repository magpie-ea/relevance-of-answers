import numpy as np
import pandas as pd
import argparse
from scipy.stats import entropy
from metrics import *
from ast import literal_eval


# This script takes the output from widen_dataframe.py or fit_beta.py
# Reshape dataframe and compute metrics: KL Utility, ER, and Bayes Factor


def compute_metrics(raw_data, prior_colname, posterior_colname):
    """
    I've set all metrics except kl and bayes_factor to lie between 0 and 1.
    :param raw_data:
    :param prior_colname:
    :param posterior_colname:
    :return:
    """
    items = raw_data
    items['first_order_belief_change'] = items.apply(lambda x: prior_posterior_distance(x[posterior_colname], x[prior_colname]), axis=1)
    items['second_order_belief_change'] = items.apply(lambda x: prior_posterior_distance(x['prior_confidence'], x['posterior_confidence']), axis=1)
    items['entropy_change'] = items.apply(lambda x: entropy_reduction(x[prior_colname], x[posterior_colname]), axis=1)
    items['kl_utility'] = items.apply(lambda x: exp10(kl(x[posterior_colname], x[prior_colname])), axis=1)
    items['bayes_factor_utility'] = items.apply(lambda x: bf_utility_polar(x[posterior_colname], x[prior_colname]), axis=1)
    items['beta_kl_utility'] = items.apply(lambda x: exp(2, kl_dirichlet(x['posterior_beta_for_kl'], x['prior_beta_for_kl'])), axis=1)
    items['beta_entropy_change'] = items.apply(lambda x: entropy_reduction_dirichlet(x['prior_beta_for_entropy'], x['posterior_beta_for_entropy']), axis=1)
    items['beta_bayes_factor_utility'] = items.apply(lambda x: beta_bayes_factor_util(x['prior_beta_for_bf'], x['posterior_beta_for_bf']), axis=1)
    items['pure_second_order_belief_change'] = items.apply(lambda x: pure_second_order_belief_change(x['prior_beta_for_2nd_order_change'], x['posterior_beta_for_2nd_order_change']), axis=1)
    return items 
    
if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="Relative path to a (widened) .csv file containing one set of participant-vignette responses per row")
    parser.add_argument("--output", help="Name of output file")
    args = parser.parse_args()
    # Read filtered data from csv
    df = pd.read_json(args.input, orient="records", lines=True)
    # Compute predictor metrics
    df = compute_metrics(df, prior_colname='prior_sliderResponse', posterior_colname='posterior_sliderResponse')
    # Get outfile
    df.to_json(args.output, orient="records", lines=True)