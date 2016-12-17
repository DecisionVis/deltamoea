"""
operators.py: definitions of MOEA search operators.
"""

def pm_inner(x_parent, x_lower, x_upper, di):
    """
    x_parent (float): between lower and upper
    x_lower (float): lower bound on dv
    x_upper (float): upper bound on dv
    di (float, nonnegative): distribution index
    """

