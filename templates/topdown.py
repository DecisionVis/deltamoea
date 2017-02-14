from moeadv import MINIMIZE
from moeadv import MAXIMIZE
from moeadv import CORNERS

from moeadv import Decision
from moeadv import Objective
from moeadv import Problem

from moeadv import create_moea_state
from moeadv import doe

# Top-down view of optimizing a 3,2 DTLZ2 with the new algorithm

decision1 = Decision("decision1", 0.0, 1.0, 0.01)
decision2 = Decision("decision2", 0.0, 1.0, 0.3)
decision3 = Decision("decision3", 0.0, 1.0, 1.0) # 0 or 1
decisions = (decision1, decision2, decision3)

objective1 = Objective("objective1", MINIMIZE)
objective2 = Objective("objective2", MINIMIZE)
objectives = (objective1, objective2)

constraints = tuple()
tagalongs = tuple()

problem = Problem(decisions, objectives, constraints, tagalongs)

# assume every call could be raising MOEAError
state = create_moea_state(problem, ranks=100, ranksize=10000)

# This is only necessary if you have individuals you've already
# evaluated.  You could delete the following three lines.
already_evaluated_individuals = tuple()
for individual in already_evaluated_individuals:
    state = return_evaluated_individual(state, individual)

# Optionally, specify alternative DOE terminating conditions.
# For the 3,2 DTLZ2 in this example, it does make sense
# because there are so few decision variables.
state = doe(state, terminate=CORNERS)

"""
for nfe in range(10000):
    state, dvs = get_sample(state)
    objs = dtlz2(dvs)
    individual = Individual(dvs, objs, tuple(), tuple())
    state = return_evaluated_individual(state, individual)

result_iterator = get_iterator(state, 0)

# the proposed C approach is very non-Pythonic, so we use a
# generator here
for individual in result_iterator:
    print(individual)

teardown(problem)
"""
