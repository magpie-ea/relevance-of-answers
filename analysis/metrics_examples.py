import pandas

from metrics import *
import pandas as pd

examples = [
    [[.8, 1], [2, 7]],
    [[.8, .8], [2, 2]],
    [[.8, .8], [2, 6]],
    [[.5, .8], [7, 2]],
    [[.8, .5], [2, 7]],
    [[.8, .2], [4, 4]],
    [[1, .8], [4, 4]],
]

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

def ec_from_p_c(ps, cs):
    conc0 = certainty_linking_function([1.76, .98], cs[0])
    conc1 = certainty_linking_function([1.76, .98], cs[1])
    prior = fit_beta_mode_concentration(ps[0], conc0)
    posterior = fit_beta_mode_concentration(ps[1], conc1)
    return entropy_reduction_dirichlet(prior, posterior)

def kl_from_p_c(ps, cs):
    conc0 = certainty_linking_function([4.83, 1.79], cs[0])
    conc1 = certainty_linking_function([4.83, 1.79], cs[1])
    prior = fit_beta_mode_concentration(ps[0], conc0)
    posterior = fit_beta_mode_concentration(ps[1], conc1)
    return kl_util_dirichlet(posterior, prior)

def bf_from_p_c(ps, cs):
    conc0 = certainty_linking_function([2.44, 3.81], cs[0])
    conc1 = certainty_linking_function([2.44, 3.81], cs[1])
    prior = fit_beta_mode_concentration(ps[0], conc0)
    posterior = fit_beta_mode_concentration(ps[1], conc1)
    return beta_bayes_factor_util(prior, posterior)

data = []
for ps, cs in examples:
    row = {
        "ec1": entropy_reduction(ps[0], ps[1]),
        "kl1": kl_util(ps[1], ps[0]),
        "bf1": bf_utility_polar(ps[0], ps[1]),
        "ec2": ec_from_p_c(ps, cs),
        "kl2": kl_from_p_c(ps, cs),
        "bf2": bf_from_p_c(ps, cs)
    }
    data.append(row)

df = pandas.DataFrame(data)
print(df)