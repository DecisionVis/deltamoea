"""
A prototype algorithmic structure that is conceived of as
being easily translated to C.  It places a priority on
minimizing allocations and other things that would be
magic in C.
"""

from problems.problems import dtlz2_rotated
from moeadv.moeadv import Decision
from moeadv.moeadv import Objective

from collections import namedtuple

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

from enum import Enum

MOEAState = Enum("MOEAState", "doe injecting evolving")

class Rank(object):
    """
    A Rank is 0 to ranksize Individuals.  Each rank is a Pareto rank, more
    or less.  In the overpopulated case where we run out of space in a rank,
    some individuals may get booted down a rank, but we'll emit a warning
    if that happens.  It's certainly not the expected case, because we plan
    on ranksize being big.
    """
    def __init__(self, ranksize, template_individual):
        self.individuals = [template_individual] * ranksize
        self.ranksize = ranksize
        self.n_individuals = 0

def index_to_point(grid, index):
    point = [grid.coordinates[c][i] for c, i
             in zip(grid.coordinates, index)]
    return tuple(point)

def point_to_index(grid, point):
    index = [max(i for i, v in enumerate(c) where v <= p)
             for p, c in zip(point, grid.coordinates)]
    return tuple(index)

def design_of_experiments(grid):
    """
    Generator method.  Produces new samples indefinitely.
    New samples are produced in decision space, not in index
    space.
    """
    # start with a center point
    lengths = tuple([len(c) for c in grid.coordinates])
    center_index = [lnth // 2 for lnth in lengths]
    center_point = index_to_point(center_index)
    yield tuple(center_point)

    # do the centers of each face and work your way out
    # to the very most extreme corners of the space
    last_index = [0] * len(grid.coordinates)
    while True:
        point = index_to_point(last_index)
        yield point

        last_index 

if __name__ == "__main__":

    evaluate = dtlz2_rotated(3,2)

    decisions = (
        Decision('x', 0.0, 1.0, 0.1),
        Decision('y', 0.0, 1.0, 0.05),
        Decision('z', 0.0, 1.0, 0.25),)
    objectives = (
        Objective('v', "min"),
        Objective('w', "min"),)
    constraints = tuple()

    # Here, we define a new custom type based on the problem definition.
    # Hey, Python, that's pretty cool!
     
    Individual = namedtuple(
        "Individual",
        [d.name for d in decisions] + [o.name for o in objectives] + [c.name for c in constraints])

    # preallocate all of the ranks
    template_individual_variables = [0 for _ in decisions] + [0.0 for _ in objectives] + [0.0 for _ in constraints]
    template_individual = Individual(*template_individual_variables)
    ranks = [Rank(10_000, template_individual) for _ in range(100)]

    grid = Grid(decisions)


    import time
    time.sleep(10)

