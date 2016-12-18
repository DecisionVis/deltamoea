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
        # Warning!  I use γ = 1-δ, since they only use 1-δ
        if x_parent > 0.5:
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
