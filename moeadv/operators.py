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
    if x_range <= 0.0:
        raise Exception(
            "Cannot define PM for non-positive range {} to {}".format(
                x_lower, x_upper))
    """
    * Let gamma = η_c+1
    * Let kappa = 1/gamma
    """
    gamma = di + 1.0
    kappa = 1.0 / gamma
    def operator(x_parent1, x_parent2):
        """
        Transform parents into normalized coordinates as follows.
        * if x_parent1 < x_parent2
            * y_1 = (x_parent1 - x_lower) / x_range
            * y_2 = (x_parent2 - x_lower) / x_range
        * otherwise
            * y_2 = (x_parent1 - x_lower) / x_range
            * y_1 = (x_parent2 - x_lower) / x_range
        """
        if x_parent1 < x_parent2:
            y_1 = (x_parent1 - x_lower) / x_range
            y_2 = (x_parent2 - x_lower) / x_range
        else:
            y_2 = (x_parent1 - x_lower) / x_range
            y_1 = (x_parent2 - x_lower) / x_range

        """
        * Let delta = y_2 - y_1
        * Let β = 1 + (2/delta) * min(y_1, 1-y_2)
        * Let α = 2 - β^{-gamma}
        """
        delta = y_2 - y_1
        beta = 1.0 + (2.0/delta) * min(y_1, 1-y_2)
        alpha = 2.0 - beta ** (-gamma)
        """
        * Let uniform_1 be a sample from the uniform random variate on [0,1].
        * if uniform_1 <= 1/α
            * β_q = (u*α)^kappa
        * otherwise
            * β_q = (1 / (2 - u*α))^kappa
        """
        uniform_1 = random.random()
        if uniform_1 <= 1.0 / alpha:
            beta_q = (uniform_1 * alpha) ** kappa
        else:
            beta_q = (1.0 / (2.0 - uniform_1 * alpha)) ** kappa
        """
        To determine which parent the child favors:
        * Let uniform_2 be another sample from the uniform random variate on [0,1].
        * If uniform_2 <= 0.5,
        * let sign = -1
        * otherwise let sign = 1.
        """
        uniform_2 = random.random()
        if uniform_2 <= 0.5:
            sign = -1.0
        else:
            sign = 1.0
        """
        y_child = 0.5[(y_1+y_2) + sign * β_q * delta]
        """
        y_child = 0.5 * ((y_1 + y_2) + sign * beta_q * delta)
        return y_child
    return operator
