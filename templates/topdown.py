import sys

from udmoea import MINIMIZE
from udmoea import MAXIMIZE
from udmoea import CORNERS
from udmoea import COUNT
from udmoea import RETAIN
from udmoea import DISCARD

from udmoea import Decision
from udmoea import Objective
from udmoea import Problem
from udmoea import Individual

from udmoea import create_moea_state
from udmoea import doe
from udmoea import get_sample
from udmoea import return_evaluated_individual
from udmoea import get_iterator

from udmoea import NearExhaustionWarning
from udmoea import TotalExhaustionError

from problems.problems import dtlz2
from problems.problems import dtlz2_rotated
from problems.problems import dtlz2_max

# Top-down view of optimizing a 4,2 DTLZ2 with the new algorithm
evaluate = dtlz2_max(4, 2)
decision1 = Decision("decision1", 0.0, 1.0, 1.0) # 0 or 1
decision2 = Decision("decision2", 0.0, 1.0, 0.3)
decision3 = Decision("decision3", 0.0, 1.0, 0.1)
decision4 = Decision("decision4", 0.0, 1.0, 0.07)
decisions = (decision1, decision2, decision3, decision4)

objective1 = Objective("objective1", MAXIMIZE)
objective2 = Objective("objective2", MAXIMIZE)
objectives = (objective1, objective2)

constraints = tuple()
tagalongs = tuple()

problem = Problem(decisions, objectives, constraints, tagalongs)

# assume every call could be raising MOEAError
state = create_moea_state(problem, ranks=100, ranksize=10000, float_values=DISCARD)

# This is only necessary if you have individuals you've already
# evaluated.  You could delete the following three lines.
already_evaluated_individuals = tuple()
for individual in already_evaluated_individuals:
    state = return_evaluated_individual(state, individual)

# Optionally, specify alternative DOE terminating conditions.
# For the 4,2 DTLZ2 in this example, it does make sense
# because there are so few decision variables.
state = doe(state, terminate=COUNT, count=10000)

for nfe in range(1, 3001):
    try:
        state, dvs = get_sample(state)
    except NearExhaustionWarning as ew:
        print("Nearly Exhausted!  Switch to exhaustive search!")
        state = ew.state
        continue
    except TotalExhaustionError as te:
        print("Totally Exhausted!  Waste electricity doing random resamples!")
        state = te.state
        continue
    except StopIteration:
        break
    if nfe % 500 == 0:
        sys.stderr.write('.')
        if nfe % 10000 == 0:
            sys.stderr.write('\n')
        elif nfe % 2500 == 0:
            sys.stderr.write(' ')
    objs = evaluate(dvs)
    individual = Individual(dvs, objs, tuple(), tuple())
    state = return_evaluated_individual(state, individual)

# Print ranks to stdout
rank_sizes = dict((ii, 0) for ii in range(len(state.archive)))
print("rank,{},{}".format(
    ",".join(d.name for d in problem.decisions),
    ",".join(o.name for o in problem.objectives)))
for ii in range(len(state.archive)):
    # the proposed C approach is very non-Pythonic, so we use a
    # generator here
    for individual in get_iterator(state, ii):
        print("{},{},{}".format(
            ii,
            ",".join("{:.2f}".format(d) for d in individual.decisions),
            ",".join("{:.2f}".format(o) for o in individual.objectives)
        ))
        rank_sizes[ii] += 1

# Print rank sizes to stderr
for ii in range(len(state.archive)):
    sys.stderr.write("{}\t{}\n".format(ii, rank_sizes[ii]))
"""
teardown(problem)
"""
