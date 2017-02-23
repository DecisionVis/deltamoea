import sys
import argparse
import random
from collections import namedtuple

from udmoea import MINIMIZE
from udmoea import MAXIMIZE
from udmoea import OFAT
from udmoea import CORNERS
from udmoea import COUNT
from udmoea import RANDOM
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

from udmoea.Functions import decisions_to_grid_point

from problems.problems import dtlz2
from problems.problems import dtlz2_rotated
from problems.problems import dtlz2_max

def the_deltas():
    yield 1.0
    yield 0.3
    yield 0.1
    yield 0.07
    while True:
        yield 0.1

def run_experiment(runtime_file, rotation_seed, udmoea_seed, nfe):
    # Top-down view of optimizing a 4,2 DTLZ2 with the new algorithm
    random.seed(rotation_seed)
    ndv = 100
    nobj = 2
    evaluate = dtlz2_rotated(ndv, nobj)
    random.seed(udmoea_seed)
    decisions = tuple(
        Decision("decision{}".format(ii), 0.0, 1.0, delta)
        for ii, delta in zip(range(ndv), the_deltas()))
    objectives = tuple(
        Objective("objective{}".format(ii), MINIMIZE)
        for ii in range(nobj))

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
    state = doe(state, terminate=COUNT, count=100)
    state = state._replace(doestate=state.doestate._replace(stage=RANDOM))

    Record = namedtuple("Record", [
        'rotation_seed',
        'moea_seed',
        'nfe',
        ] + [
        "grid{}".format(d) for d in range(ndv)] + [
        "decision{}".format(d) for d in range(ndv)] + [
        "objective{}".format(o) for o in range(nobj)] + [
        "grid_objective{}".format(o) for o in range(nobj)])
    with open("{}.header.csv".format(runtime_file.name), 'w') as fp:
        fp.write(",".join(Record._fields))
        fp.write("\n")
    for ii in range(1, nfe):
        try:
            state, dvs = get_sample(state)
        except NearExhaustionWarning as ew:
            print("Nearly Exhausted!  Switch to exhaustive search!")
            state = ew.state
            continue
        except TotalExhaustionError as te:
            print("Totally Exhausted!  Escape!")
            state = te.state
            break
        except StopIteration:
            break
        if ii % 500 == 0:
            sys.stderr.write('.')
            if ii % 10000 == 0:
                sys.stderr.write('\n')
            elif ii % 2500 == 0:
                sys.stderr.write(' ')
        objs = evaluate(dvs)
        individual = Individual(dvs, objs, tuple(), tuple())
        state = return_evaluated_individual(state, individual)

        grid_point = decisions_to_grid_point(state.grid, dvs)

        record = Record(*([
            "{}".format(rotation_seed),
            "{}".format(udmoea_seed),
            "{}".format(ii),] + [
            "{}".format(g) for g in grid_point] + [
            "{:.4f}".format(d) for d in dvs] + [
            "{:.4f}".format(o) for o in objs] + [
            "{:.4f}".format(o) for o in objs]
        ))
        runtime_file.write("{}\n".format(",".join(record)))
        if nfe % 50 == 0:
            runtime_file.flush()

    # Print rank 0
    for individual in get_iterator(state, 0):
        grid_point = decisions_to_grid_point(state.grid, individual.decisions)
        record = Record(*([
            "{}".format(rotation_seed),
            "{}".format(udmoea_seed),
            "{}".format(nfe),] + [
            "{}".format(g) for g in grid_point] + [
            "{:.4f}".format(d) for d in individual.decisions] + [
            "{:.4f}".format(o) for o in individual.objectives] + [
            "{:.4f}".format(o) for o in individual.objectives]
        ))
        print("{}".format(",".join(record)))
    rank_sizes = dict((ii, 0) for ii in range(len(state.archive)))
    for ii in range(len(state.archive)):
        # the proposed C approach is very non-Pythonic, so we use a
        # generator here
        for individual in get_iterator(state, ii):
            rank_sizes[ii] += 1
    # Print rank sizes to stderr
    for ii in range(len(state.archive)):
        sys.stderr.write("{}\t{}\n".format(ii, rank_sizes[ii]))

def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("runtime_file", type=argparse.FileType('a'))
    parser.add_argument("rotation_seed", type=int, help="seed for generating a random rotation matrix for dtlz2")
    parser.add_argument("udmoea_seed", type=int, help="seed for UDMOEA's RNG")
    parser.add_argument("NFE", type=int, help="length of run")
    args = parser.parse_args()

    run_experiment(
        args.runtime_file,
        args.rotation_seed,
        args.udmoea_seed,
        args.NFE)

if __name__ == "__main__":
    cli()
