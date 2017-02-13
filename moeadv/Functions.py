from collections import namedtuple
from moeadv.Structures import Rank
from moeadv.Structures import Individual
from moeadv.Constants import MAXIMIZE
from moeadv.Constants import MINIMIZE

def _create_archive(problem, ranks, ranksize):
    # construct bogus individuals to fill the archive
    bogus_decisions = tuple((999 for _ in problem.decisions))
    bogus_objectives = list()
    # in C, math.h has macros for infinity and nan
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
    bogus_individual = Individual(
        bogus_decisions,
        bogus_objectives,
        bogus_constraints,
        bogus_tagalongs)
    # Construct an archive full of references to the bogus individual
    archive = tuple((
        Rank([bogus_individual for _ in range(ranksize)], 0)
        for _ in range(ranks)
    ))
    return archive

def create_moea_state(problem, **kwargs):
    """
    problem (Problem): definition of problem structure.

    keywords:
        ranks (int): number of ranks to allocate in the archive
                     (default 100)
        ranksize (int): number of individuals in a rank
                     (default 10,000)

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
    ranks = kwargs.get('ranks', 100)
    ranksize = kwargs.get('ranksize', 10000)
    archive = _create_archive(problem, ranks, ranksize)

    state = MOEAState(
        problem,
        archive
    )
    return state
