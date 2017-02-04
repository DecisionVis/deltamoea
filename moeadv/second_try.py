"""
A prototype algorithmic structure that is conceived of as
being easily translated to C.  It places a priority on
minimizing allocations and other things that would be
magic in C.
"""

from problems.problems import dtlz2_rotated
from moeadv.moeadv import Decision
from moeadv.moeadv import Objective

evaluate = dtlz2_rotated(3,2)

decisions = (
    Decision('x', 0.0, 1.0, 0.1),
    Decision('y', 0.0, 1.0, 0.05),
    Decision('z', 0.0, 1.0, 0.25),)
objectives = (
    Objective('v', "min"),
    Objective('w', "min"),)
constraints = tuple()

from collections import namedtuple

Individual = namedtuple(
    "Individual",
    [d.name for d in decisions] + [o.name for o in objectives] + [c.name for c in constraints])


