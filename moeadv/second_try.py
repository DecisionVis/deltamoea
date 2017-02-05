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

# Here, we define a new custom type based on the problem definition.
# Hey, Python, that's pretty cool!
 
Individual = namedtuple(
    "Individual",
    [d.name for d in decisions] + [o.name for o in objectives] + [c.name for c in constraints])

# Next, just allocate a big array to hold the Individuals.
# In C, we'd make it an array of structs, but in Python we
# don't have that option, so we're going to go column wise.

def array_size(the_decisions):
    decision = the_decisions[0]
    range = decision.upper - decision.lower
    decision_size = range / decision.delta
    # special (but common) case: range is evenly divided by decisions
    # (This is going to come up a lot, isn't it?  We don't just want
    # to compute array size, we also want to compute actual grid points.
    if abs(decision_size * delta - range) / range <= 1e-6:

    if len(the_decisions) == 1:
        return decision_size
    else:
        return decision_size * array_size(the_decisions[1:]

decision_sizes = list()

for decision in decisions:
    decision_size = 
