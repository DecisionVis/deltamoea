"""
operators.py: definitions of MOEA search operators.
"""

from random import random
from math import ceil
from math import floor

def pm_delta(x_lower, x_upper, delta, di):
    _operator = pm_inner(x_lower, x_upper, di)
    def operator(x_parent):
        x_child_continuous = _operator(x_parent)
        continuous_delta = x_child_continuous - x_parent
        if continuous_delta == 0:
            x_child_unchecked = x_parent - delta
        elif continuous_delta < 0:
            deltas = floor(continuous_delta / delta)
            x_child_unchecked = x_parent - deltas * delta
        else:
            deltas = ceil(continuous_delta / delta)
            x_child_unchecked = x_parent + deltas * delta
        if x_child_unchecked < x_lower:
            x_child = x_lower
        elif x_child_unchecked > x_upper:
            x_child = x_upper
        else:
            x_child = x_child_unchecked
        return x_child
    return operator

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
    if di < 0:
        raise Exception(
            "PM is not defined for negative values of distribution index.")
    alpha = di + 1
    exponent = 1.0 / alpha
    def operator(x_parent):
        x_parent_scaled = (x_parent - x_lower) / (x_upper - x_lower)
        # Warning!  I use γ = 1-δ, since they only use 1-δ
        if x_parent_scaled > 0.5:
            gamma = x_parent_scaled
        else:
            gamma = 1.0 - x_parent_scaled
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
            "Cannot define SBX for non-positive range {} to {}".format(
                x_lower, x_upper))
    if di < 0.0:
        raise Exception(
            "SBX is not defined for negative values of distribution index.")
    gamma = di + 1.0
    kappa = 1.0 / gamma
    def operator(x_parent1, x_parent2):
        if x_parent1 == x_parent2:
            # early return if parents are the same
            return x_parent1
        swapped = False
        if x_parent1 < x_parent2:
            y_1 = (x_parent1 - x_lower) / x_range
            y_2 = (x_parent2 - x_lower) / x_range
        else:
            swapped = True
            y_2 = (x_parent1 - x_lower) / x_range
            y_1 = (x_parent2 - x_lower) / x_range
        delta = y_2 - y_1
        beta = 1.0 + (2.0/delta) * min(y_1, 1-y_2)
        alpha = 2.0 - beta ** (-gamma)
        uniform_1 = random()
        if uniform_1 <= 1.0 / alpha:
            beta_q = (uniform_1 * alpha) ** kappa
        else:
            beta_q = (1.0 / (2.0 - uniform_1 * alpha)) ** kappa
            # This assertion is not true! assert(beta_q <= 1.0)
        if swapped:
            sign = -1.0
        else:
            sign = 1.0
        y_child = 0.5 * ((y_1 + y_2) + sign * beta_q * delta)
        x_child = x_lower + x_range * y_child
        return x_child
    return operator
