import re
import pandas as pd
from scipy.stats import beta, entropy, pearsonr
from scipy.special import loggamma, digamma, gamma
import random
import numpy as np
from scipy.optimize import minimize
from metrics import *
import math
import argparse

def fit_beta_mode_concentration(mode, concentration):
    """
    Compute parameters from the mode and concentration following this parameterization:
    https://en.wikipedia.org/wiki/Beta_distribution#Mode_and_concentration
    """
    alpha = mode * (concentration-2) + 1
    beta = (1-mode) * (concentration-2) + 1
    return alpha, beta


def certainty_linking_function(x, certainty):
    return x[0] * (x[1] ** certainty)


def objective_function_exp_concentration_map(x, df):
    def map_certainty_to_concentration_local(certainty):
        return certainty_linking_function(x, certainty)

    # for field in ["prior", "posterior"]:
    prior = df.apply(lambda z: fit_beta_mode_concentration(z[f"prior_sliderResponse"],
                                                                map_certainty_to_concentration_local(z[f"prior_confidence"])), axis=1)
    posterior = df.apply(lambda z: fit_beta_mode_concentration(z[f"posterior_sliderResponse"],
                                                                map_certainty_to_concentration_local(z[f"posterior_confidence"])), axis=1)

    r = [kl_util_dirichlet(post, pre) for pre, post in zip(prior, posterior)]
    try:
        to_return = -1 * pearsonr(df["relevance_sliderResponse"], r)[0]
    except ValueError:
        to_return = np.inf
    return to_return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    df = pd.read_json(args.input, orient="records", lines=True)
    x = minimize(lambda x: objective_function_exp_concentration_map(x, df),
                 method='SLSQP',
                 x0=np.array([3, 3]),
                 bounds=[(0, np.inf), (0, np.inf)]
                 ).x
    # a, b = x.x[0], x.x[1]
    for p in ["prior", "posterior"]:
        df[f"{p}_concentration"] = df[f"{p}_confidence"].apply(lambda c: certainty_linking_function(x, c))
        df[f"{p}_beta"] = df.apply(lambda x: fit_beta_mode_concentration(x[f"{p}_sliderResponse"], x[f"{p}_concentration"]), axis=1)
        df.drop(f"{p}_concentration", axis=1)

    output = args.output if args.output else args.input
    df.to_json(output, orient="records", lines=True)
