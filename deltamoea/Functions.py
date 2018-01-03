"""
Copyright (c) 2018 DecisionVis, LLC. All rights reserved.

Redistribution and use in source and binary forms, with
or without modification, are permitted provided that the
following conditions are met:

1. Redistributions of source code must retain the above
copyright notice, this list of conditions and the following
disclaimer.

2. Redistributions in binary form must reproduce the
above copyright notice, this list of conditions and the
following disclaimer in the documentation and/or other
materials provided with the distribution.

3. Neither the name of the copyright holder nor the names
of its contributors may be used to endorse or promote
products derived from this software without specific prior
written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER
OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""

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
from .Structures import Issue
from .Structures import Issued
from .Structures import MOEAState

from .Sorting import sort_into_archive

from .Sampling import doe_next
from .Sampling import evolve
from .Sampling import NearExhaustionWarning
from .Sampling import TotalExhaustionError

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
    issued = Issued(
        [Issue(grid.GridPoint(*(-1 for _ in problem.decisions)), False)
         for _ in range(ranksize)],
        0,
        set())
    # This is a placeholder.  We call doe() below to
    # initialize the doe state.
    doestate = DOEState(RANDOM, COUNT, 0, 0)

    state = MOEAState(
        problem,
        float_values,
        grid,
        archive,
        set(), # archive_set for Python acceleration
        rank_A,
        rank_B,
        issued,
        _random,
        _randint,
        doestate
    )
    state = doe(state)
    return state

def doe(state, **kwargs):
    """
    Return an MOEAState such that the next generated
    samples will begin to fill out a design of experiments
    on the decision space, rather than doing evolution
    on the archived individuals.  If this function is not
    called, we will do COUNT 100 by default.

    The DOE proceeds as:
        corners         (2 ^ ndv samples)
        center point    (1 sample)
        OFAT            (2 * ndv samples)
        random uniform  (unlimited samples)

    If a different DOE procedure works better for your problem,
    you may substitute one of your choosing by running the
    DOE separately and supplying evaluated individuals to
    the algorithm using return_evaluated_individual before
    beginning the evolution run.

    keywords:
        terminate (CENTERPOINT, OFAT, CORNERS, COUNT):
            indicates stage after which to switch from
            DOE to evolution. Defaults to COUNT 100, which
            means 100 random samples will be generated
            before evolution starts.  If you have a lot
            of decision variables and choose CORNERS,
            you may never finish doing your DOE, but if
            you have a small number of decision variables
            it may be worth while.
            If you specify COUNT, then the number of DOE samples
            is determined by the "count" keyword argument.
        count (int): Number of DOE samples to perform, if COUNT
            is specified as a DOE termination condition.
            Default is ndv.
        stage (CORNERS, CENTERPOINT, OFAT, RANDOM): at which
            stage to start sampling.
    """
    terminate = kwargs.get("terminate", COUNT)
    stage = kwargs.get("stage", RANDOM)
    if terminate == COUNT:
        default_count = len(state.problem.decisions)
        count = kwargs.get("count", default_count)
    else:
        count = 0
    old_doestate = state.doestate
    new_doestate = old_doestate._replace(
        terminate=terminate,
        stage=stage,
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
    archive_set = state.archive_set
    archive_set.add(grid_point)
    state = state._replace(archive_set=archive_set)
    issues = state.issued.issues
    for ii in range(len(issues)):
        issue = issues[ii]
        if issue.outstanding and issue.grid_point == grid_point:
            issues[ii] = issue._replace(outstanding=False)
            issued_set = state.issued.issued_set
            issued_set.remove(grid_point)
            # These _replace calls are not strictly necessary
            # because we're mutating internal structures, but
            # I have a "don't change without calling _replace" rule
            # for myself.
            issued = state.issued._replace(
                issues=issues,
                issued_set=issued_set)
            state = state._replace(issued=issued)
            break

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

def get_sample(state):
    """
    state (MOEAState): current algorithm state

    Returns a new MOEAState and a sample in decision space.
    """
    # Should we do a DOE sample?
    if _should_do_doe(state):
        state, grid_point = doe_next(state)
        # Only DOE samples performed here count against the
        # COUNT termination condition.  (It's perfectly legit
        # for a user to call doe_next to get DOE samples in
        # other circumstances.)
        if state.doestate.terminate == COUNT and state.doestate.remaining > 0:
            state = state._replace(doestate=state.doestate._replace(
                    remaining=state.doestate.remaining - 1))
    else:
        state, grid_point = evolve(state)

    # Add grid_point to issued list
    issues = state.issued.issues
    index = state.issued.index
    issues[index] = Issue(grid_point, True)
    issued_set = state.issued.issued_set
    issued_set.add(grid_point)
    state = state._replace(
        issued=state.issued._replace(
            issues=issues,
            issued_set=issued_set,
            index=(index + 1) % len(issues)
    ))

    grid = state.grid
    sample = grid.Sample(*(a[i] for a, i in zip(grid.axes, grid_point)))
    # Return sample
    return state, sample

def _should_do_doe(state):
    """
    state (MOEAState)
    Returns True if we should do a DOE sample.

    The termination condition is terminate-after-stage,
    so if you specify CENTERPOINT as your termination
    condition, you get one DOE sample.  The way to get
    zero DOE samples is to set the termination condition
    to COUNT and the count to 0.  If the archive is
    completely empty, we're going to issue DOE samples
    anyway, so the user shouldn't be asking for samples
    in that situation if DOE samples are not desired.
    """
    stage = state.doestate.stage
    terminate = state.doestate.terminate
    if terminate == COUNT:
        return state.doestate.remaining > 0
    elif stage == CENTERPOINT:
        return True
    elif stage == OFAT:
        return terminate in (OFAT, CORNERS)
    elif stage == CORNERS:
        return terminate == CORNERS
    elif stage == RANDOM:
        # You're only going to get random points if you're
        # using COUNT for your termination condition.  Or
        # if we've issued a ton of points and gotten none
        # back.
        return False
    # True is safer than False as a fallback, because you
    # can always do DOE but you can't always do selection
    # and variation.  Nevertheless, this return statement
    # should be unreachable.
    return True

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


