"""
Copyright (c) 2017 DecisionVis, LLC. All rights reserved. 

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

import sys
import argparse
import random
from collections import namedtuple

from deltamoea import MINIMIZE
from deltamoea import MAXIMIZE
from deltamoea import OFAT
from deltamoea import CORNERS
from deltamoea import COUNT
from deltamoea import RANDOM
from deltamoea import RETAIN
from deltamoea import DISCARD

from deltamoea import Decision
from deltamoea import Objective
from deltamoea import Problem
from deltamoea import Individual

from deltamoea import create_moea_state
from deltamoea import doe
from deltamoea import get_sample
from deltamoea import return_evaluated_individual
from deltamoea import get_iterator

from deltamoea import NearExhaustionWarning
from deltamoea import TotalExhaustionError

from deltamoea import decisions_to_grid_point

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

def run_experiment(runtime_file, rotation_seed, dmoea_seed, nfe):
    random.seed(rotation_seed)
    ndv = 100
    nobj = 2
    evaluate = dtlz2_rotated(ndv, nobj)
    random.seed(dmoea_seed)
    decisions = tuple(
        Decision("decision{}".format(ii), 0.0, 1.0, delta)
        for ii, delta in zip(range(ndv), the_deltas()))
    objectives = tuple(
        Objective("objective{}".format(ii), MINIMIZE)
        for ii in range(nobj))

    constraints = tuple()
    tagalongs = tuple()

    problem = Problem(decisions, objectives, constraints, tagalongs)

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

    Record = namedtuple("Record", [
        'rotation_seed',
        'moea_seed',
        'nfe',
        ] + [
        "grid{}".format(d) for d in range(ndv)] + [
        "decision{}".format(d) for d in range(ndv)] + [
        "objective{}".format(o) for o in range(nobj)])
    # write the header only if file is empty
    if runtime_file.tell() == 0:
        runtime_file.write(",".join(Record._fields))
        runtime_file.write("\n")
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
            "{}".format(dmoea_seed),
            "{}".format(ii),] + [
            "{}".format(g) for g in grid_point] + [
            "{:.4f}".format(d) for d in dvs] + [
            "{:.4f}".format(o) for o in objs]
        ))
        runtime_file.write("{}\n".format(",".join(record)))
        if nfe % 50 == 0:
            runtime_file.flush()

    # Print rank 0
    print(",".join(Record._fields))
    for individual in get_iterator(state, 0):
        grid_point = decisions_to_grid_point(state.grid, individual.decisions)
        record = Record(*([
            "{}".format(rotation_seed),
            "{}".format(dmoea_seed),
            "{}".format(nfe),] + [
            "{}".format(g) for g in grid_point] + [
            "{:.4f}".format(d) for d in individual.decisions] + [
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
    parser.add_argument("dmoea_seed", type=int, help="seed for DMOEA's RNG")
    parser.add_argument("NFE", type=int, help="length of run")
    args = parser.parse_args()

    run_experiment(
        args.runtime_file,
        args.rotation_seed,
        args.dmoea_seed,
        args.NFE)

if __name__ == "__main__":
    cli()
