import pandas

from metrics import *
import pandas as pd

examples = [
    [[.9, 1], [3, 7]],
    [[.8, .8], [2, 2]],
    [[.8, .8], [2, 6]],
    [[.8, .9], [7, 2]],
    [[.9, .8], [2, 7]],
    [[.8, .2], [4, 4]],
    [[1, .8], [4, 4]],



    # [[.45, .55], [2, 6]],
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

# def certainty_linking_joint(certainty):
#     return 5.65243178 * (1.38574103 ** certainty)


# joint = [2.00000000000000,1.8887878870680397,2.0057878939477938]
# x_ec = [2.003132909367684,2.099619465796772,2.182282698193184]
# x_kl = [2.0916418583650374,1.8941737720648337,2.7268183206235452]
# x_bf = [1.9094156433165135,1.4780033232425207,1.7430067992449518]
# x_so = [1.4901599742496174,1.5244523784328503,1.1941668791591107]

x_kl2 = [2.0916418583650374,1.8941737720648337,2.7268183206235452]
x_ec2 = [2.003132909367684,2.099619465796772,2.182282698193184]
x_bf2 = [3.203002096813438,5.191727560937999,1.1396952026480702]
x_pu2 = [1.4901599742496174,1.5244523784328503,1.1941668791591107]
x_kl1 = [2.0,2.0,885603.8574641224]
x_ec1 = [2.0,2.0,1154.7269694164272]


def ec_from_p_c(ps, cs):
    conc0 = certainty_linking_function(x_ec2, cs[0])
    conc1 = certainty_linking_function(x_ec2, cs[1])
    prior = fit_beta_mode_concentration(ps[0], conc0)
    posterior = fit_beta_mode_concentration(ps[1], conc1)
    return g(entropy_reduction_dirichlet(prior, posterior), x_ec2[2])

def kl_from_p_c(ps, cs):
    conc0 = certainty_linking_function(x_kl2, cs[0])
    conc1 = certainty_linking_function(x_kl2, cs[1])
    prior = fit_beta_mode_concentration(ps[0], conc0)
    posterior = fit_beta_mode_concentration(ps[1], conc1)
    return g(kl_util_dirichlet(posterior, prior), x_kl2[2])

def bf_from_p_c(ps, cs):
    conc0 = certainty_linking_function(x_bf2, cs[0])
    conc1 = certainty_linking_function(x_bf2, cs[1])
    prior = fit_beta_mode_concentration(ps[0], conc0)
    posterior = fit_beta_mode_concentration(ps[1], conc1)
    return g(beta_bayes_factor_util_1(prior, posterior), x_bf2[2])

data = []
for ps, cs in examples:
    row = {
        "ec1": g(entropy_reduction(ps[0], ps[1]), x_ec1[2]),
        "kl1": g(kl(ps[1], ps[0]), x_kl1[2]),
        "bf1": bf_utility_polar(ps[0], ps[1]),
        "ec2": ec_from_p_c(ps, cs),
        "kl2": kl_from_p_c(ps, cs),
        "bf2": bf_from_p_c(ps, cs)
    }
    data.append(row)

df = pandas.DataFrame(data)
print(df.to_latex(index=False, float_format="%.2f"))