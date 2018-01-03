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

from .Constants import MAXIMIZE
from .Constants import MINIMIZE
from .Constants import LEFT_DOMINATES
from .Constants import RIGHT_DOMINATES
from .Constants import NEITHER_DOMINATES

from math import isnan

def sort_into_archive(state, archive_individual):
    archive = state.archive

    rank_A = state.rank_A._replace(occupancy=0)
    rank_B = state.rank_B._replace(occupancy=0)

    # rank A will always be the one we're sorting into
    # the next archive rank, and rank B will be the
    # recipient of displaced individuals.
    rank_A.individuals[0] = archive_individual
    rank_A = rank_A._replace(occupancy=1)

    rank_into = 0
    # loop over archive ranks
    while rank_A.occupancy > 0 and rank_into + 1 < len(archive):
        into = archive[rank_into]
        # print("----")
        # print("before: rank {}".format(rank_into))
        # _print_rank(into)
        # print("before: rank_A")
        # _print_rank(rank_A)
        # print("before: rank_B")
        # _print_rank(rank_B)
        # loop over rank A
        a_remaining = rank_A.occupancy
        for ai, a_ind in enumerate(rank_A.individuals):
            # print("processing {} from rank A: {}".format(ai, a_ind))
            if a_remaining <= 0:
                break
            if not a_ind.valid:
                continue
            a_remaining -= 1
            # loop over rank being sorted into
            i_remaining = into.occupancy
            for ii, i_ind in enumerate(into.individuals):
                if i_remaining <= 0:
                    break
                if not i_ind.valid:
                    continue
                i_remaining -= 1
                dominance = _compare(a_ind, i_ind)
                # invalidate the dominated individual 
                # insert it into rank_B
                # adjust rank occupancy
                if dominance == LEFT_DOMINATES:
                    rank_B, into = move_individual(
                        rank_B, rank_B.occupancy, into, ii)
                elif dominance == RIGHT_DOMINATES:
                    rank_B, rank_A = move_individual(
                        rank_B, rank_B.occupancy, rank_A, ai)
                    # break if rank A individual was dominated and go
                    # to next rank A individual
                    break
        # print("after comparisons: rank {}".format(rank_into))
        # _print_rank(into)
        # print("after comparisons: rank_A")
        # _print_rank(rank_A)
        # print("after comparisons: rank_B")
        # _print_rank(rank_B)
        # insert valid individuals from rank A in "into"
        into, rank_A = fill_rank_from_rank(into, rank_A)

        # print("after fill: rank {}".format(rank_into))
        # _print_rank(into)
        # print("after fill: rank_A")
        # _print_rank(rank_A)
        # print("after fill: rank_B")
        # _print_rank(rank_B)

        # insert overflow in rank B
        rank_B, rank_A = fill_rank_from_rank(rank_B, rank_A)

        # print("after overflow: rank {}".format(rank_into))
        # _print_rank(into)
        # print("after overflow: rank_A")
        # _print_rank(rank_A)
        # print("after overflow: rank_B")
        # _print_rank(rank_B)

        # swap rank A and rank B
        rank_B, rank_A = rank_A, rank_B
        # update the archive
        archive[rank_into] = into

        # print("after: rank {}".format(rank_into))
        # _print_rank(into)
        # print("after: rank_A")
        # _print_rank(rank_A)
        # print("after: rank_B")
        # _print_rank(rank_B)

        rank_into += 1

    # insert all remaining overflow in the last rank
    last_rank = archive[-1]
    last_rank, rank_A = fill_rank_from_rank(last_rank, rank_A)
    archive[-1] = last_rank

    # if there's anything left in rank A, discard the grid points
    # from the archive set
    archive_set = state.archive_set
    for arch_ind in rank_A.individuals:
        if arch_ind.valid:
            archive_set.difference_update((arch_ind.grid_point,))

    state = state._replace(
        rank_A=rank_A,
        rank_B=rank_B,
        archive=archive,
        archive_set=archive_set)

    return state

def _print_rank(rank):
    print("occupancy {}".format(rank.occupancy))
    print("valid {}".format(sum((1 for i in rank.individuals if i.valid))))
    ii = 0
    valid = 0
    while valid < rank.occupancy and ii < len(rank.individuals):
        print(rank.individuals[ii])
        if rank.individuals[ii].valid:
            valid += 1
        ii += 1

def fill_rank_from_rank(destination, source):
    di = 0
    for si, s_ind in enumerate(source.individuals):
        if source.occupancy <= 0:
            break
        if not s_ind.valid:
            continue
        if destination.occupancy >= len(destination.individuals):
            break
        while di < len(destination.individuals):
            if destination.individuals[di].valid:
                di += 1
            else:
                destination, source = move_individual(
                    destination, di, source, si)
                break
        if di >= len(destination.individuals):
            break
    return destination, source

def move_individual(destination_rank, destination_index, source_rank, source_index):
    """
    Move an archive individual from one rank to another rank.
    This function does not check bounds or make any other safety guarantees.
    This function assumes that the individual is valid and adjusts
    occupancy accordingly.

    destination_rank (Rank)
    destination_index (int): index into destination_rank
    source_rank (Rank)
    source_index (int): index into source_rank

    Returns an updated destination rank and source rank.
    """
    individual = source_rank.individuals[source_index]
    destination_rank.individuals[destination_index] = individual
    destination_rank = destination_rank._replace(
        occupancy=destination_rank.occupancy + 1)
    source_rank.individuals[source_index] = individual._replace(
        valid=False)
    source_rank = source_rank._replace(
        occupancy=source_rank.occupancy - 1)
    return destination_rank, source_rank

def _compare(left, right):
    """
    left (Individual)
    right (Individual)
    """
    dleft = True
    dright = True
    # compare 
    for zl, zr in zip(left.constraints, right.constraints):
        if zl <= 0 and zr <= 0:
            # For constraints, we are indifferent to values
            # less than zero.
            continue
        if isnan(zl):
            dleft = False
        if isnan(zr):
            dright = False
        if dleft and zl > zr:
            dleft = False
        elif dright and zr > zl:
            dright = False
        if not (dleft or dright):
            # Early return!! No point in continuing because both
            # individuals violate constraints and neither one
            # dominates the other.
            return NEITHER_DOMINATES
    if dleft and not dright:
        return LEFT_DOMINATES
    if dright and not dleft:
        return RIGHT_DOMINATES

    # Both individuals are feasible, so compare objectives.
    for yl, yr in zip(left.objectives, right.objectives):
        if isnan(yl):
            dleft = False
        if isnan(yr):
            dright = False
        # minimize everything
        if yl > yr:
            dleft = False
        elif yr > yl:
            dright = False
        if not (dleft or dright):
            # early return!!
            return NEITHER_DOMINATES
    if dleft and not dright:
        return LEFT_DOMINATES
    elif dright and not dleft:
        return RIGHT_DOMINATES
    else:
        # if we've oversampled and the individuals are
        # nondominated, arbitrarily say that the
        # "left" individual dominates
        if left.grid_point == right.grid_point:
            return LEFT_DOMINATES
        else:
            return NEITHER_DOMINATES

