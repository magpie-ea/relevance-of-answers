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
    items['kl'] = items.apply(lambda x: kl(x[posterior_colname], x[prior_colname]), axis=1)
    items['kl_util'] = items.apply(lambda x: exp10(kl(x[posterior_colname], x[prior_colname])), axis=1)
    items['entropy_reduction'] = items.apply(lambda x: entropy_reduction(x[prior_colname], x[posterior_colname]), axis=1)
    items['bayes_factor'] = items.apply(lambda x: bayes_factor(x[posterior_colname], x[prior_colname]), axis=1)
    items['exp_bayes_factor'] = items.apply(lambda x: exp_bayes_factor(x[posterior_colname], x[prior_colname]), axis=1)
    items['posterior_distance'] = items.apply(lambda x: posterior_distance(x[posterior_colname]), axis=1)
    items['prior_posterior_distance'] = items.apply(lambda x: prior_posterior_distance(x[posterior_colname], x[prior_colname]), axis=1)
    items['kl_beta'] = items.apply(lambda x: kl_dirichlet(x['posterior_beta'], x['prior_beta']), axis=1)
    items['kl_util_beta'] = items.apply(lambda x: exp(2, kl_dirichlet(x['posterior_beta'], x['prior_beta'])), axis=1)
    items['entropy_reduction_beta'] = items.apply(lambda x: entropy_reduction_dirichlet(x['prior_beta'], x['posterior_beta']), axis=1)
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