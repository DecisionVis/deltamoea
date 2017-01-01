"""
test-problems.py

Tests for test problems.
"""
from problems.problems import dtlz2
import random

def test_dtlz2_range():
    """
    test that dtlz2 produces objectives in a reasonable range.
    Minimum: 0 (inclusive)
    Maximum: 1 + 0.25 * (1+n-M) where n is number of DVs and M
    is number of objectives
    """
    for nobj in range(2, 11):
        for ndv in range(nobj, nobj+10):
            upper_limit = 1 + 0.25 * (1 + ndv - nobj)
            evaluate = dtlz2(ndv, nobj)
            for counter in range(1000):
                xx = [random.random() for _ in range(ndv)]
                yy = evaluate(xx)
                assert(len(yy) == nobj)
                for ii, objective in enumerate(yy):
                    if objective < 0:
                        print("nobj {} ndv {} counter {} objective {} is {} < 0".format(
                            nobj, ndv, counter, ii, objective))
                    if objective > upper_limit:
                        print("nobj {} ndv {} counter {} objective {} is {} > {}".format(
                            nobj, ndv, counter, ii, objective, upper_limit))


