"""
test-pm.py

Tests for Polynomial Mutation
"""

from moeadv.operators import pm_inner
from random import random

def test_pm_range():
    for di in [15, 10, 0, 1, 100]:
        for scale in [1, 1e-6, 1e6, 1e-12, 1e12, 1e-24, 1e24]:
            x_lower = random() * scale
            x_upper = x_lower + random() * (scale - x_lower)
            operator = pm_inner(x_lower, x_upper, di)
            for ii in range(100):
                x_parent = x_lower + random() * (x_upper - x_lower)
                x_child = operator(x_parent)
                if not x_lower < x_child < x_upper:
                    raise Exception("{} < {} < {} parent {} di {} scale {} iteration {}".format(
                        x_lower, x_child, x_upper, x_parent, di, scale, ii)
                        )
