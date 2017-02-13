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
state = create_moea_state(problem, options)

for individual in already_evaluated_individuals:
    state = return_evaluated_individual(state, individual)
state = doe(state)

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



