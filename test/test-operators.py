"""
test-operators.py

Tests for search operators
"""

from moeadv.operators import pm_inner
from moeadv.operators import pm_delta
from moeadv.operators import sbx_inner
from random import random
from random import randint

def test_pm_range():
    for di in (15, 10, 0, 1, 100):
        for scale in (1, 1e-6, 1e6, 1e-12, 1e12, 1e-24, 1e24):
            for offset in (0, 0.001, 1, 100, 1e8):
                scaled_offset = offset * scale
                x_lower = scaled_offset + random() * scale
                x_upper = scaled_offset + x_lower + random() * (scale - x_lower)
                operator = pm_inner(x_lower, x_upper, di)
                for ii in range(1000):
                    x_parent = x_lower + random() * (x_upper - x_lower)
                    x_child = operator(x_parent)
                    if not x_lower <= x_child <= x_upper:
                        raise Exception("{} < {} < {} parent {} di {} scale {} offset {} iteration {}".format(
                            x_lower, x_child, x_upper, x_parent, di, scale, scaled_offset, ii)
                            )
def test_pm_delta_range():
    for di in (15, 10, 0, 1, 100):
        for scale in (1, 1e-6, 1e6, 1e-12, 1e12, 1e-24, 1e24):
            for offset in (0, 0.001, 1, 100, 1e8):
                scaled_offset = offset * scale
                x_lower = scaled_offset + random() * scale
                x_upper = scaled_offset + x_lower + random() * (scale - x_lower)
                deltas = randint(1,100)
                delta = (x_upper - x_lower) * 1.0 / deltas
                operator = pm_delta(x_lower, x_upper, delta, di)
                for ii in range(1000):
                    x_parent = x_lower + random() * (x_upper - x_lower)
                    x_child = operator(x_parent)
                    if not x_lower <= x_child <= x_upper:
                        raise Exception("{} < {} < {} ({}) parent {} di {} scale {} offset {} iteration {}".format(
                            x_lower, x_child, x_upper, delta, x_parent, di, scale, scaled_offset, ii)
                            )
def test_sbx_range():
    for di in (15, 10, 0, 1, 100):
        for scale in (1, 1e-6, 1e6, 1e-12, 1e12, 1e-24, 1e24):
            for offset in (0, 0.001, 1, 100, 1e8):
                scaled_offset = offset * scale
                x_lower = scaled_offset + random() * scale
                x_upper = scaled_offset + x_lower + random() * (scale - x_lower)
                assert(x_lower < x_upper)
                operator = sbx_inner(x_lower, x_upper, di)
                for ii in range(1000):
                    x_parent1 = x_lower + random() * (x_upper - x_lower)
                    x_parent2 = x_lower + random() * (x_upper - x_lower)
                    try:
                        x_child = operator(x_parent1, x_parent2)
                    except AssertionError as ae:
                        print("{} < {} parent {} parent {} di {} scale {} offset {} iteration {}".format(
                            x_lower, x_upper, x_parent1, x_parent2, di, scale, scaled_offset, ii)
                            )
                        raise
                    if not x_lower <= x_child <= x_upper:
                        raise Exception("{} < {} parent {} parent {} di {} scale {} offset {} iteration {}".format(
                            x_lower, x_upper, x_parent1, x_parent2, di, scale, scaled_offset, ii)
                            )
