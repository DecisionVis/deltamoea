from collections import namedtuple

from math import floor

from random import random
from random import randint

from .Constants import MAXIMIZE
from .Constants import MINIMIZE

from .Constants import CENTERPOINT
from .Constants import OFAT
from .Constants import CORNERS
from .Constants import RANDOM
from .Constants import COUNT

from .Constants import RETAIN
from .Constants import DISCARD

from .Structures import Rank
from .Structures import Individual
from .Structures import ArchiveIndividual
from .Structures import DOEState
from .Structures import Axis
from .Structures import Grid
from .Structures import GridPoint
from .Structures import MOEAState

from .Sorting import sort_into_archive

def create_moea_state(problem, **kwargs):
    """
    problem (Problem): definition of problem structure.

    keywords:
        ranks (int): number of ranks to allocate in the archive
                     (default 100)
        ranksize (int): number of individuals in a rank
                     (default 10,000)
        float_values (RETAIN or DISCARD): what to do with decision
                     variable values.  If RETAIN is selected,
                     the decision variable values will be stored
                     along with the grid points of every individual.
                     If there is a large number of decision variables,
                     this policy results in greatly increased storage
                     requirements, and may require a reduction in
                     ranks or ranksize for the archive to fit in
                     memory.  RETAIN may be a desirable behavior if
                     you are doing local optimization or providing
                     individuals that have been evaluated on a
                     different grid. 
                     If DISCARD is selected, the decision variable
                     values for each individual will not be stored
                     explicitly, and will be regenerated from the
                     individual's grid point.  As long as the
                     individuals provided to the algorithm were
                     evaluated at grid points in decision space, this
                     option is lossless and saves a lot of space.
                     DISCARD is the default for this option.
        random (callable): a real-number generating function,
                     returning a number on the interval [0,1).
                     If none is provided, we fall back on
                     Python's random.random.
        randint (callable): an integer generating function
                     taking two arguments, a lower bound and
                     an (inclusive) upper bound, and returning
                     a number within those bounds.  E.g.
                     calling intrand(0, 1) should return 0 or
                     1.  We expect this to be a random number
                     generator and the algorithm may not
                     converge if it is not.  If not provided,
                     we fall back on Python's random.randint.

    This function creates MOEA state, including
    pre-allocation of a large archive for individuals.

    If the individuals are very large, it may make sense
    to reduce ranks or ranksize to avoid an unnecessary
    allocation.  This entails a tradeoff: fewer ranks save
    memory but risk forgetting that a badly dominated
    point in decision space has already been sampled.
    Smaller ranksize can save a great deal of memory
    if selected appropriately, at the risk of degrading
    algorithmic performance when ranks overflow.
    """
    float_values = kwargs.get("float_values", DISCARD)
    ranks = kwargs.get('ranks', 100)
    ranksize = kwargs.get('ranksize', 10000)
    _random = kwargs.get('random', random)
    _randint = kwargs.get('randint', randint)
    grid = _create_grid(problem.decisions)
    archive = [_empty_rank(problem, float_values, ranksize)
               for _ in range(ranks)]
    rank_A = _empty_rank(problem, float_values, ranksize)
    rank_B = _empty_rank(problem, float_values, ranksize)
    issued = tuple(
        (tuple((-1 for _ in problem.decisions))
        for _ in range(ranksize)))
    # initial DOE state is: do an OFAT DOE
    doestate = DOEState(CENTERPOINT, OFAT, 0, 0)

    state = MOEAState(
        problem,
        float_values,
        grid,
        archive,
        rank_A,
        rank_B,
        issued,
        _random,
        _randint,
        doestate
    )
    return state

def doe(state, **kwargs):
    """
    Return an MOEAState such that the next generated
    samples will begin to fill out a design of experiments
    on the decision space, rather than doing evolution
    on the archived individuals.  If this function is not
    called and initial evaluated samples are not provided,
    some DOE samples will still be generated until there
    is material for evolution.

    The DOE proceeds as:
        center point    (1 sample)
        OFAT            (2 * ndv samples)
        corners         (2 ^ ndv samples)
        random uniform  (unlimited samples)

    If a different DOE procedure works better for your problem,
    you may substitute one of your choosing by running the
    DOE separately and supplying evaluated individuals to
    the algorithm using return_evaluated_individual before
    beginning the evolution run.

    keywords:
        terminate (CENTERPOINT, OFAT, CORNERS, COUNT):
            indicates stage after which to switch from
            DOE to evolution. Defaults to OFAT, which
            means 2 * ndv + 1 samples will be generated
            before evolution starts.  If you have a lot
            of decision variables and choose CORNERS,
            you may never finish doing your DOE, but if
            you have a small number of decision variables
            it may be worth while.
            If you specify COUNT, then the number of DOE samples
            is determined by the "count" keyword argument.
        count (int): Number of DOE samples to perform, if COUNT
            is specified as a DOE termination condition.
            Default is 2 * ndv + 1.
    """
    terminate = kwargs.get("terminate", OFAT)
    if terminate == COUNT:
        default_count = 2 * len(state.problem.decisions) + 1
        count = kwargs.get("count", default_count)
    else:
        count = 0
    old_doestate = state.doestate
    new_doestate = old_doestate._replace(
        terminate=terminate,
        remaining=count)
    new_state = state._replace(doestate=new_doestate)
    return new_state

def return_evaluated_individual(state, individual):
    """
    Return an MOEAState that accounts for the provided
    Individual.
    """
    # produce an ArchiveIndividual from the Individual
    if state.float_values == RETAIN:
        decisions = individual.decisions
    else:
        decisions = tuple()
    grid_point = decisions_to_grid_point(state.grid, individual.decisions)
    # ArchiveIndividuals always sort with < and we reverse the transformation
    # when returning Individuals.
    problem = state.problem
    objectives = list()
    for ob, value in zip(problem.objectives, individual.objectives):
        if ob.sense == MINIMIZE:
            objectives.append(value)
        else:
            objectives.append(-value)
    # Ditto constraints
    constraints = list()
    for co, value in zip(problem.constraints, individual.constraints):
        if co.sense == MINIMIZE:
            constraints.append(value)
        else:
            constraints.append(-value)
    archive_individual = ArchiveIndividual(
        True,
        grid_point,
        decisions,
        tuple(objectives),
        tuple(constraints),
        individual.tagalongs)

    # sort the ArchiveIndividual into the archive
    state = sort_into_archive(state, archive_individual)

    # return the state
    return state

def decisions_to_grid_point(grid, decisions):
    """
    grid (Grid): map between the axes and the 
    decisions (tuple of floats): decision variable values

    Returns the GridPoint corresponding to the decisions.
    """
    indices = list()
    for axis, delta, value in zip(grid.axes, grid.deltas, decisions):
        if value <= axis[0]:
            indices.append(0)
        elif value >= axis[-1]:
            indices.append(len(axis) - 1)
        else:
            # return whatever index is closest
            under = int(floor((value - axis[0])/delta))
            under_value = axis[under]
            over_value = axis[under + 1]
            if value - under_value <= over_value - value:
                indices.append(under)
            else:
                indices.append(under + 1)
    return grid.GridPoint(*indices)

def get_iterator(state, rank_number):
    """
    Generator that iterates over the solutions in a rank.
    """
    axes = state.grid.axes
    o_coefficients = list()
    for objective in state.problem.objectives:
        if objective.sense == MAXIMIZE:
            o_coefficients.append(-1)
        else:
            o_coefficients.append(1)
    c_coefficients = list()
    for constraint in state.problem.constraints:
        if constraint.sense == MAXIMIZE:
            c_coefficients.append(-1)
        else:
            c_coefficients.append(1)
    for a_individual in state.archive[rank_number].individuals:
        if a_individual.valid:
            sample = state.grid.Sample(
                *(a[i] for a, i in zip(axes, a_individual.grid_point)))
            objectives = [y * c for y, c
                          in zip(a_individual.objectives, o_coefficients)]
            constraints = [y * c for y, c
                          in zip(a_individual.constraints, c_coefficients)]
            individual = Individual(
                sample,
                objectives,
                constraints,
                a_individual.tagalongs)
            yield individual

def _dummy_grid_sample(grid):
    """ generator function, placeholder for selection and
    variation operators, and DOE, just returns all grid
    points in no particularly good order. """
    index = grid.GridPoint(*(0 for _ in grid.axes))
    while True:
        yield index
        new_index = list()
        overflow = True
        # treat first index as least significant because
        # it's easiest that way
        for ii, axis in zip(index, grid.axes):
            if overflow:
                if ii+1 < len(axis):
                    new_index.append(ii+1)
                    overflow = False
                else:
                    new_index.append(0)
                    overflow = True
            else:
                new_index.append(ii)
        if overflow:
            raise StopIteration()
        index = grid.GridPoint(*new_index)

dgs = None
def get_sample(state):
    """
    state (MOEAState): current algorithm state

    Returns a new MOEAState and a sample in decision space.
    """
    # bootstrapping the algorithm: for now use grid sampling as
    # a placeholder
    global dgs
    if dgs is None:
        dgs = _dummy_grid_sample(state.grid)
    grid_point = next(dgs)
    sample = state.grid.Sample(*(a[i] for a, i in zip(state.grid.axes, grid_point)))
    return state, sample

def _create_grid(decisions):
    """
    decisions: tuple of Decisions

    Returns a Grid corresponding to the Decisions.
    """
    # Defining a new namedtuple here as a convenience, and
    # mainly so that it's readable in debugging prints.
    _Axes = namedtuple("Axes", (d.name for d in decisions))

    axes = list()
    for decision in decisions:
        decision_range = decision.upper - decision.lower
        number_of_intervals = int(floor(decision_range / decision.delta))
        span = number_of_intervals * decision.delta
        if span + decision.delta - decision_range < 1e-6 * decision.delta:
            # If floor cut us off really close to the upper limit,
            # we need to include it.
            corrected_number_of_intervals = number_of_intervals + 1
            lower = decision.lower
        else:
            # Divide the slop by two and use it as a margin.
            corrected_number_of_intervals = number_of_intervals
            lower = decision.lower + 0.5 * (decision_range - span)
        # accumulate grid values
        values = list()
        value = lower
        for ii in range(corrected_number_of_intervals + 1):
            values.append(value)
            value += decision.delta
        # correct last value to exactly the upper limit because
        # floating point math can accumulate errors
        if values[-1] > decision.upper:
            values[-1] = decision.upper
        axis = Axis(values)
        axes.append(axis)
    _Deltas = namedtuple("Deltas", (d.name for d in decisions))
    grid = Grid(
        _Axes(*axes),
        _Deltas(*(d.delta for d in decisions)),
        namedtuple("GridPoint", (d.name for d in decisions)),
        namedtuple("Sample", (d.name for d in decisions))
    )
    return grid

def _empty_rank(problem, float_values, ranksize):
    # construct bogus individuals to fill the rank
    bogus_grid_point = tuple((999 for _ in problem.decisions))
    if float_values == RETAIN:
        bogus_decisions = tuple((0.0 for _ in problem.decisions))
    else:
        bogus_decisions = tuple()
    bogus_objectives = list()
    # in C99, math.h has macros for infinity and nan
    inf = float("inf")
    ninf = -inf
    # Bogus individuals should never dominate true individuals.
    for objective in problem.objectives:
        if objective.sense == MAXIMIZE:
            bogus_objectives.append(ninf)
        else:
            bogus_objectives.append(inf)
    # Nor should they appear even remotely feasible.
    bogus_constraints = list()
    for constraint in problem.constraints:
        if constraint.sense == MAXIMIZE:
            bogus_constraints.append(ninf)
        else:
            bogus_constraints.append(inf)
    bogus_tagalongs = list((0.0 for _ in problem.tagalongs))
    bogus_archive_individual = ArchiveIndividual(
        False, # and bogus individuals are invalid
        bogus_grid_point,
        bogus_decisions,
        bogus_objectives,
        bogus_constraints,
        bogus_tagalongs)
    return Rank([bogus_archive_individual for _ in range(ranksize)], 0)


