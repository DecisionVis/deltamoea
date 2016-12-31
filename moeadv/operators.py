"""
operators.py: definitions of MOEA search operators.
"""

from random import random

def pm_inner(x_lower, x_upper, di):
    """
    Returns an "inner" PM operator.  I.e. a PM operator for a single variable.

    x_lower (float): lower bound on dv
    x_upper (float): upper bound on dv
    di (float, nonnegative): distribution index
    """
    x_range = x_upper - x_lower
    if x_range <= 0:
        raise Exception(
            "Cannot define PM for non-positive range {} to {}".format(
                x_lower, x_upper))
    alpha = di + 1
    exponent = 1.0 / alpha
    def operator(x_parent):
        x_parent_scaled = (x_parent - x_lower) / (x_upper - x_lower)
        assert(0 <= x_parent_scaled <= 1)
        # Warning!  I use γ = 1-δ, since they only use 1-δ
        if x_parent_scaled > 0.5:
            gamma = x_parent_scaled
        else:
            gamma = 1.0 - x_parent_scaled
        assert(0.5 <= gamma)
        assert(gamma <= 1.0)
        uniform = random() # on [0,1]
        beta = (gamma ** alpha) * (1 - 2 * uniform)
        if uniform <= 0.5:
            exponand = 2 * uniform + beta
            delta_q = exponand ** exponent - 1
        else:
            exponand = 2 * (1.0 - uniform) - beta
            delta_q = 1 - exponand ** exponent
        x_child_scaled = x_parent_scaled + delta_q
        x_child = x_child_scaled * x_range + x_lower
        return x_child
    return operator

def sbx_inner(x_lower, x_upper, di):
    """
    Returns an "inner" SBX operator.  I.e. an SBX operator for
    a single variable.
    x_lower (float): lower bound on DV
    x_upper (float): upper bound on DV
    di (float, nonnegative): distribution index
    """
    x_range = x_upper - x_lower
    if x_range <= 0:
        raise Exception(
            "Cannot define PM for non-positive range {} to {}".format(
                x_lower, x_upper))
    gamma = di + 1.0
    kappa = 1.0 / gamma
    def operator(x_parent1, x_parent2):

    """
    1.
    * Let uniform_1 be a sample from the uniform random variate on [0,1].

    2.
    * Let gamma = η_c+1
    * Let kappa = 1/gamma

    Transform parents into normalized coordinates as follows.

    * if x_parent1 < x_parent2
        * y_1 = (x_parent1 - x_lower) / x_range
        * y_2 = (x_parent2 - x_lower) / x_range
    * otherwise
        * y_2 = (x_parent1 - x_lower) / x_range
        * y_1 = (x_parent2 - x_lower) / x_range

    * Let delta = y_2 - y_1
    * Let α = 2 - β^{-gamma}
    * Let β = 1 + (2/delta) * min(y_1, 1-y_2)
    * if uniform_1 <= 1/α
        * β_q = (u*α)^kappa
    * otherwise
        * β_q = (1 / (2 - u*α))^kappa

    Here, the parameter y is assumed to vary in [0,1].

    3.
    Let uniform_2 be another sample from the uniform random variate on [0,1].
    If uniform_2 <= 0.5,
    let sign = -1
    otherwise let sign = 1.

    y_child = 0.5[(y_1+y_2) + sign * β_q * delta]
    """

