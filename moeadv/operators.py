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

    """
    1. Create a random number `u` between 0 and 1.
    2. Find a parameter β_q using a polynomial probability
    distribution, developed in [Deb and Agrawal 1995] from a
    schema processing point of view, as follows:

    β_q = (uα)^\frac{1}{η_c+1} if u <= 1/α
    β_q = \frac{1}{2-uα}^\frac{1}{η_c+1} otherwise

    where α = 2 - β^{-(η_c+1)}
    and β = 1 + \frac{2}{y_2-y_1}min[(y_1-y_l),(y_u-y_2)]

    Here, the parameter y is assumed t vary in [y_l, y_u].
    The parameter η_c is the distribution index for SBX
    and can take any non-negative value.  A small value
    of η_c allows solutions far away from parents to be
    created as children solutions and a large value
    restricts only near-parent solutions to be created
    as children solutions.

    3. The children solutions are then calculated as follows:
    c_1 = 0.5[(y_1+y_2) - β_q|y_2-y_1|]
    c_2 = 0.5[(y_1+y_2) + β_q|y_2-y_1|]

    It is assumed here that y_1 < y_2.  A simple modification
    to the above equation can be made for y_1 > y_2.  For
    handling multiple variables, each variable is chosen
    with a probability 0.5 and the above SBX operator is
    applied variable-by-variable.  In all simulation results
    here, we have used η_c = 1.
    """

