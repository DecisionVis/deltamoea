"""
A prototype algorithmic structure that is conceived of as
being easily translated to C.  It places a priority on
minimizing allocations and other things that would be
magic in C.
"""

from problems.problems import dtlz2_rotated

evaluate = dtlz2_rotated(3,2)

decisions = (
    Decision('x', 0.0, 1.0, 0.1),
    Decision('y', 0.0, 1.0, 0.05),
    Decision('z', 0.0, 1.0, 0.25),)
objectives = (
    Objective('v', "minimize"),
    Objective('w', "maximize"),)
constraints = tuple()

if __name__ == "__main__":


