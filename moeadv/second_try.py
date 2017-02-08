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
from random import randint

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
    point = [c[i] for c, i
             in zip(grid.coordinates, index)]
    return tuple(point)

def point_to_index(grid, point):
    index = [max(i for i, v in enumerate(c) if v <= p)
             for p, c in zip(point, grid.coordinates)]
    return tuple(index)

def design_of_experiments(grid):
    """
    Generator method.  Produces new samples indefinitely.
    New samples are produced in decision space, not in index
    space.  May eventually start repeating itself.

    The design is:
        first the center point (1 point)
        then the middle of each face (2 * d points)
        then each corner of the hypercube (2^d points)
        then random points (indefinitely)
    """
    lengths = tuple([len(c) for c in grid.coordinates])

    # center point
    center_index = [length // 2 for length in lengths]
    center_point = index_to_point(grid, center_index)
    yield center_point

    # middle of faces
    for ii, length in enumerate(lengths):
        index_lo = [c for c in center_index]
        index_lo[ii] = 0
        point_lo = index_to_point(grid, index_lo)
        yield point_lo

        index_hi = [c for c in center_index]
        index_hi[ii] = length - 1
        point_hi = index_to_point(grid, index_hi)
        yield point_hi

    # corners
    ndim = len(lengths)
    counter = 0
    while counter < (1 << len(lengths)):
        index = [0 for _ in lengths]
        for ii, length in enumerate(lengths):
            mask = 1 << ii
            if counter & mask != 0:
                index[ii] = length - 1
        counter += 1
        point = index_to_point(grid, index)
        yield point

    # random points
    while True:
        index = [randint(0, length-1) for length in lengths]
        point = index_to_point(grid, index)
        yield point

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

    # do initial design of experiments
    state = MOEAState.doe
    doe = design_of_experiments(grid)

    for _ in range(30):
        print([round(100*x) for x in next(doe)])

    import time
    time.sleep(1)

