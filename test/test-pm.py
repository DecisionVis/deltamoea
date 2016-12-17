"""
test-pm.py

Tests for Polynomial Mutation
"""

from moeadv.operators import pm_inner
from random import random

def test_pm_range():
    for di in [0, 1, 10, 100]:
        for scale in [1e-24, 1e-12, 1e-6, 1, 1e6, 1e12, 1e24]:
            x_lower = random() * scale
            x_upper = x_lower + random() * (scale - x_lower)
            x_parent = x_lower + random() * (x_upper - x_lower)
            x_child = pm_inner(x_parent, x_lower, x_upper, di)
            if not (x_lower < x_child < x_parent):
                assert(False)
