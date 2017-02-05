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

class Grid(object):
    """
    Define the coordinates for the grid.  (Not the whole grid, but
    the points on each axis.)
    """
    def __init__(self, decisions):
        # Why tuples: This is a promise to myself about immutability.
        # The coordinates may neither grow nor change once determined.
        coordinates = list()
        for decision in decisions:
            points = list()
            xx = decision.lower
            while xx < decision.upper + (decision.upper - decision.lower) * 1e-6:
                points.append(xx)
                xx += decision.delta
            coordinates.append(tuple(points))
        self.coordinates = tuple(coordinates)

grid = Grid(decisions)

# Now we allocate an array to hold individuals.  To get in the spirit,
# we're going to fill it in advance.

size_of_grid = 1
for axis in grid.coordinates:
    size_of_grid *= len(axis)

MAX_INDIVIDUALS = 10_000_000 # ten million!

template_individual_variables = [0 for _ in decisions] + [0.0 for _ in objectives] + [0.0 for _ in constraints]
template_individual = Individual(*template_individual_variables)
individuals_received = 0
individuals = [template_individual] * MAX_INDIVIDUALS

# archive and population are just indices into the individuals array?


import time
time.sleep(10)

