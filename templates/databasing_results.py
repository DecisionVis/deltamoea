import sqlite3
import uuid
import subprocess
import time

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
    yield 0.3
    yield 0.1
    yield 0.07
    yield 1.0 # this used to be first, but it really messes with nonrotated DTLZ2
    while True:
        yield 0.1

def run_experiment(connection, rotation_seed, udmoea_seed, nfe):
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
    #state = doe(state, terminate=COUNT, count=100)

    run_id = str(uuid.uuid4().bytes)
    Run = namedtuple("Run", (
        "run_id",
        "problem_id",
        "target_nfe",
        "algorithm",
        "commit_id",
        "prng_seed"))

    try:
        git = subprocess.Popen(
            ['git', 'diff', '--stat'],
            stdout=subprocess.PIPE)
        diffsize = git.stdout.read()
        git = subprocess.Popen(
            ['git', 'log', '-n1', '--format=%h,%s'],
            stdout=subprocess.PIPE)
        commit_id, comment = git.stdout.read().decode('ASCII').strip().split(",")
        git.wait()
        if len(diffsize) > 0:
            sys.stderr.write("Warning! Uncommitted changes.\n")
            commit_id = "modified {}".format(commit_id)
    except Exception as ee: # any sort of failure
        sys.stderr.write("Unknown git status, full speed ahead!!!\n")
        sys.stderr.write("{}".format(ee))
        commit_id = ""
        comment = ""

    run = Run(run_id, 1, nfe, "UDMOEA", commit_id, udmoea_seed)
    connection.execute("INSERT INTO runs values (?,?,?,?,?,?)", run)
    starttime = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(time.time()))
    connection.execute("INSERT INTO starts values (?, ?)", (run_id, starttime))

    Record = namedtuple("Record", [
        "run_id",
        'nfe',
        ] + [
        "grid{}".format(d) for d in range(ndv)] + [
        "decision{}".format(d) for d in range(ndv)] + [
        "objective{}".format(o) for o in range(nobj)] + [
        "grid_objective{}".format(o) for o in range(nobj)])

    query = "INSERT INTO evaluations_dtlz2_rot_100_2_0 VALUES ({})".format(",".join(["?"] * len(Record._fields)))

    reason = "Completed"
    nfe_performed = 0
    try:
        for ii in range(1, nfe+1):
            try:
                state, dvs = get_sample(state)
            except NearExhaustionWarning as ew:
                print("Nearly Exhausted!  Switch to exhaustive search!")
                state = ew.state
                continue
            except TotalExhaustionError as te:
                print("Totally Exhausted!  Escape!")
                state = te.state
                reason = "Exhausted"
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
                run_id,
                "{}".format(ii),] + [
                "{}".format(g) for g in grid_point] + [
                "{:.4f}".format(d) for d in dvs] + [
                "{:.4f}".format(o) for o in objs] + [
                "{:.4f}".format(o) for o in objs]
            ))
            connection.execute(query, record)
            if ii % 1000 == 0:
                connection.commit()
            nfe_performed += 1
    except Exception as ee:
        reason = str(type(ee))

    endtime = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(time.time()))
    connection.execute("INSERT INTO completions values (?, ?, ?, ?)",
        (run_id, endtime, nfe_performed, reason))
    connection.commit()

def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("dbfile", type=str)
    parser.add_argument("rotation_seed", type=int, help="seed for generating a random rotation matrix for dtlz2")
    parser.add_argument("udmoea_seed", type=int, help="seed for UDMOEA's RNG")
    parser.add_argument("NFE", type=int, help="length of run")
    args = parser.parse_args()

    connection = sqlite3.connect(args.dbfile)
    run_experiment(
        connection,
        args.rotation_seed,
        args.udmoea_seed,
        args.NFE)

if __name__ == "__main__":
    cli()

