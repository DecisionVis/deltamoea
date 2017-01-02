"""
test-problems.py

Tests for test problems.
"""
from problems.problems import dtlz2
from problems.problems import uniform_random_dv_rotation
from problems.problems import dtlz2_rotated
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
                        raise Exception("nobj {} ndv {} counter {} objective {} is {} < 0".format(
                            nobj, ndv, counter, ii, objective))
                    if objective > upper_limit:
                        raise Exception("nobj {} ndv {} counter {} objective {} is {} > {}".format(
                            nobj, ndv, counter, ii, objective, upper_limit))

def test_rotate():
    """
    test that vectors still have the same length after rotation
    """
    for ndv in range(2, 30):
        for aa in range(10):
            print("ndv {} aa {}".format(ndv, aa))
            rotate = uniform_random_dv_rotation(ndv)
            for bb in range(10):
                xx = [random.random() for _ in range(ndv)]
                xlength = sum(x**2 for x in xx) ** 0.5
                yy = rotate(xx)
                ylength = sum(y**2 for y in yy) ** 0.5
                if abs(xlength - ylength) > 1e-6:
                    raise Exception(
                        "ndv {} rotation {} iteration {} xx {} yy {} xlength {} ylength {}".format(
                            ndv, aa, bb, xx, yy, xlength, ylength))


def test_rotated_dtlz2_range():
    """
    test that rotated dtlz2 produces objectives in a reasonable range.
    """
    for nobj in range(2, 11):
        for ndv in range(nobj, nobj+10):
            upper_limit = 1 + 0.25 * (1 + ndv - nobj)
            evaluate = dtlz2_rotated(ndv, nobj)
            for counter in range(1000):
                xx = [random.random() for _ in range(ndv)]
                yy = evaluate(xx)
                assert(len(yy) == nobj)
                for ii, objective in enumerate(yy):
                    if objective < 0:
                        raise Exception("nobj {} ndv {} counter {} objective {} is {} < 0".format(
                            nobj, ndv, counter, ii, objective))
                    if objective > upper_limit:
                        raise Exception("nobj {} ndv {} counter {} objective {} is {} > {}".format(
                            nobj, ndv, counter, ii, objective, upper_limit))
