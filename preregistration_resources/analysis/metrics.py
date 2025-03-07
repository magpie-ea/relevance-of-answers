import numpy as np
import math
from scipy.stats import entropy
from scipy.special import loggamma, digamma, gamma

def kl(p, q):
    """
    :param p: posterior
    :param q: prior
    :return:
    """
    return entropy([p, 1-p], [q, 1-q], base=2)

def exp10(x):
    return 1 - (10 ** (-1 * x))

def exp(b, x):
    return 1 - (b ** (-1 * x))

def kl_util(p, q):
    """
    :param p: posterior
    :param q: prior
    :return:
    """
    return exp10(entropy([p, 1-p], [q, 1-q], base=2))

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
        return 1
    else:
        return (np.float64(p) / (1-p)) * (np.float64(1-q) / q)

def log_bayes_factor(p, q):
    """
    :param p: posterior
    :param q: prior
    :return: absolute value of log of bayes factor
    """
    if p == 1 and q == 1 or p == 0 and q == 0:
        return 0
    else:
        return abs(np.log10(bayes_factor(p, q)))

def bf_utility_polar(p, q):
    """
    :param p: posterior
    :param q: prior
    """
    if p > q:
        p = 1 - p
        q = 1 - q
    return 1 - bayes_factor(p, q)

def bf_utility_multi_avg(p_list, q_list):
    """
    Note: This equals bf_utility_polar for 2-alt questions, but doesn't work when there are >2 alts.
    For example, if the i^{th} alternative is always 0, that still brings down the average.
    :param p_list:
    :param q_list:
    :return:
    """
    utils = []
    for p, q in zip(p_list, q_list):
        utils.append(bf_utility_polar(p, q))
    return np.mean(utils)

def bf_utility_multi_weighted_avg(p_list, q_list):
    """
    Note:
    :param p_list:
    :param q_list:
    :return:
    """
    utils = []
    for p, q in zip(p_list, q_list):
        utils.append(p * bf_utility_polar(p, q))
    return sum(utils)



# def exp_bayes_factor(p, q):
#     """
#     :param p: posterior
#     :param q: prior
#     :return: expontential transformation of absolute value of log of bayes factor
#     NOTE: See simpler closed form above
#     """
    # if p == 1 and q == 1 or p == 0 and q == 0:
    #     return 0
    # else:
    #     return exp10(abs(np.log10((np.float64(p) / (1-p)) * (np.float64(1-q) / q))))



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

def kl_dirichlet(Q, P):
    """
    :param Q: posterior params for dirichlet dist.
    :param P: prior params for dirichlet dist.
    Compute KL(Q; P) divergence of 2 dirichlet distributions with parameters Q and P.
    As usual, with KL(Q; P) Q represents the posterior, and P the prior.
    When these are beta distributions, Q[0] = \alpha, Q[1] = \beta.
    """
    return loggamma(sum(Q)) - loggamma(sum(P)) + \
        sum([loggamma(p) - loggamma(q) for p, q in zip(P, Q)]) + \
        sum([(q - p) * (digamma(q) - digamma(sum(Q))) for p, q in zip(P, Q)])


def kl_util_dirichlet(Q, P):
    """
    :param Q: posterior params for dirichlet dist.
    :param P: prior params for dirichlet dist.
    Compute KL(Q; P) divergence of 2 dirichlet distributions with parameters Q and P.
    As usual, with KL(Q; P) Q represents the posterior, and P the prior.
    When these are beta distributions, Q[0] = \alpha, Q[1] = \beta.
    """
    return exp(2, kl_dirichlet(Q, P))

def entropy_dirichlet(P):
    """
    Compute Entropy H(P) of a dirichlet distribution with parameters P.
    When P is a beta distributions, P[0] = \alpha, P[1] = \beta.
    Note: Differential entropy (i.e. continuous generalization of entropy) can be negative:
    Read more: https://en.wikipedia.org/wiki/Differential_entropy
    https://en.wikipedia.org/wiki/Beta_distribution#Quantities_of_information_(entropy)
    """
    a0 = sum(P)
    try:
        to_return = math.log(math.prod([gamma(a) for a in P]) / gamma(a0)) \
               + (a0 - len(P)) * digamma(a0) \
               - sum([(p - 1) * digamma(p) for p in P])

        if np.isnan(to_return):
            to_return = -5
    except ValueError:
        to_return = -5
    return to_return


def entropy_reduction_dirichlet(P, Q):
    """
    :param P: prior params for dirichlet dist.
    :param Q: posterior params for dirichlet dist.
    :return: Entropy reduction
    """
    return abs(entropy_dirichlet(P) - entropy_dirichlet(Q))


def beta_bayes_factor(P, Q):
    """
    :param P: prior params for dirichlet dist.
    :param Q: posterior params for dirichlet dist.
    :return:
    """
    return abs(P[0] - Q[0]) + abs(P[1] - Q[1])


def beta_bayes_factor_util(P, Q):
    """
    :param P: prior params for dirichlet dist.
    :param Q: posterior params for dirichlet dist.
    :return:
    """
    return math.log(beta_bayes_factor(P, Q) + 2)


def pure_second_order_belief_change(P, Q):
    """
    :param P: prior params for dirichlet dist.
    :param Q: posterior params for dirichlet dist.
    :return:
    """
    return abs(P[0] + P[1] - (Q[0] + Q[1]))