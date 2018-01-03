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

# DOEState stages
from .Constants import CENTERPOINT
from .Constants import OFAT
from .Constants import CORNERS
from .Constants import RANDOM
from .Constants import EXHAUSTIVE
from .Constants import EXHAUSTED

from math import floor
from math import ceil

class NearExhaustionWarning(Exception):
    def __init__(self, state, *args, **kwargs):
        super(NearExhaustionWarning, self).__init__(*args, **kwargs)
        self.state = state

class TotalExhaustionError(Exception):
    def __init__(self, state, *args, **kwargs):
        super(TotalExhaustionError, self).__init__(*args, **kwargs)
        self.state = state

def is_duplicate(state, grid_point):
    if grid_point in state.issued.issued_set:
        return True
    if grid_point in state.archive_set:
        return True
    #for rank in state.archive:
    #    counter = 0
    #    for arch_ind in rank.individuals:
    #        if counter >= rank.occupancy:
    #            break
    #        if arch_ind.valid:
    #            counter += 1
    #            if grid_point == arch_ind.grid_point:
    #                return True
    return False

def doe_next(state):
    """
    state (MOEAstate)

    Return the next DOE grid point and update state accordingly.
    Will raise an exception if random sampling is having
    trouble finding a free grid point.
    Will raise another exception if a full grid sweep is
    unable to find a free grid point.  Users would be well
    advised to stop after the first exception!  After the
    second exception, we have to start duplicating samples.
    """
    doestate = state.doestate
    stage = doestate.stage
    grid = state.grid
    duplicated = True
    duplicates_generated = 0
    while duplicated:
        if stage == CENTERPOINT:
            grid_point = grid.GridPoint(*(len(a) // 2 for a in grid.axes))
            doestate = doestate._replace(stage=OFAT, counter=0)
        elif stage == OFAT:
            indices = [len(a) // 2 for a in grid.axes]
            counter = doestate.counter
            axis_index = counter // 2 # two points per axis
            axis = grid.axes[axis_index]
            if counter % 2 == 0:
                # low side sample
                indices[axis_index] = 0
            else:
                # high side sample
                indices[axis_index] = len(axis) - 1
            grid_point = grid.GridPoint(*indices)
            advanced_counter = counter + 1
            if advanced_counter // 2 >= len(grid.axes):
                doestate = doestate._replace(stage=RANDOM, counter=0)
            else:
                doestate = doestate._replace(counter=advanced_counter)
        elif stage == CORNERS:
            # Treat the counter like a bitvector, where 0 means low and 1
            # means high.  Because it's easy to write this way, treat
            # axis 0 as the LSB.
            indices = list()
            for ii, axis in enumerate(grid.axes):
                bit = (doestate.counter >> ii) & 1
                if bit == 0:
                    indices.append(0)
                else:
                    indices.append(len(axis) - 1)
            grid_point = grid.GridPoint(*indices)
            advanced_counter = doestate.counter + 1
            if advanced_counter >= 2 ** len(grid.axes):
                doestate = doestate._replace(stage=CENTERPOINT, counter=0)
            else:
                doestate = doestate._replace(counter=advanced_counter)
        elif stage in (RANDOM, EXHAUSTED):
            grid_point = grid.GridPoint(
                *(state.randint(0, len(a) - 1) for a in grid.axes))
            # transition out of RANDOM is if we have too many failures
            doestate = doestate._replace(counter=doestate.counter + 1)
        elif stage == EXHAUSTIVE:
            # Decompose the counter into indices, again treating axis
            # 0 as the least significant because it's easy to write.
            # This also takes advantage of the fact that Python has
            # bignums.  In C we need to check overflow,
            # although if we overflow 2 ** 63 - 1, that means
            # we've sampled almost 1e19 grid points.  So good
            # for us, if we trip over that condition!
            indices = list()
            counter = doestate.counter
            total_points = 1
            for axis in grid.axes:
                alen = len(axis)
                total_points = total_points * alen # mind overflow here!
                indices.append(counter % alen)
                counter = counter // alen
            advanced_counter = doestate.counter + 1
            if advanced_counter >= total_points:
                doestate = doestate._replace(stage=EXHAUSTED, counter=0)
                state = state._replace(doestate=doestate)
                raise TotalExhaustionError(state)
            else:
                doestate = doestate._replace(counter=advanced_counter)
        if stage == EXHAUSTED:
            # No point in wasting time on a duplicate check, and
            # if we're exhausted the loop condition will remain true
            # forever.
            break
        duplicated = is_duplicate(state, grid_point)
        if duplicated and stage == RANDOM:
            duplicates_generated += 1
            # How hard do we want to try here?  This says if the space
            # is more than 99.9% sampled on average we should move over
            # to exhaustive search.
            if duplicates_generated > 1000:
                doestate = doestate._replace(stage=EXHAUSTIVE)
                state = state._replace(doestate=doestate)
                raise NearExhaustionWarning(state)
    state = state._replace(doestate=doestate)
    return state, grid_point

def evolve(state):
    """
    state (MOEAState)

    This function produces a grid point by performing selection and
    variation.  It is the primary means by which we search for
    superior individuals in the problem space.
    """
    total_archive_occupancy = sum(r.occupancy for r in state.archive)
    # if archive is too small, return doe_next
    if total_archive_occupancy < 2:
        return doe_next(state)
    randint = state.randint

    # Ramp is greater than -1, and it determines how likely each rank
    # is to be selected for Parent B.
    ramp = -1

    duplicated = True
    circuit_breaker = 0
    while duplicated and circuit_breaker < 10:
        # Select parent A from rank 0.  Parents A and B are grid points.
        parent_a = _select(state, 0)
        if randint(1, 10) == 1:
            # do continuous injection
            draw = randint(0, 99)
            breaks = (10,30,60,80,90,95,100)
            n_dv_to_modify = 1
            for ii, limit in enumerate(breaks):
                count = ii + 1
                if draw >= limit or count == len(parent_a):
                    n_dv_to_modify = count
                    break
            offspring = parent_a
            while n_dv_to_modify > 0:
                n_dv_to_modify -= 1
                dv_index = randint(0, len(parent_a) - 1)
                while offspring[dv_index] != parent_a[dv_index]:
                    # don't repeat yourself
                    dv_index = randint(0, len(parent_a) - 1)
                axis = state.grid.axes[dv_index]
                field = offspring._fields[dv_index]
                # uniform random mutation, different sense
                # of the word "index"
                new_index = randint(0, len(axis) - 2)
                # cut a hole for the current index
                # (hence the -2 above)
                if new_index >= offspring[dv_index]:
                    new_index += 1
                offspring = offspring._replace(**{field: new_index})
        else:
            # do SBX
            parent_b = parent_a
            while parent_b == parent_a:
                # Choose a rank for parent B.  Parent B's role is not symmetrical
                # with parent A, unlike in traditional SBX.  This selection-and-
                # variation procedure uses one or two variables from Parent B to mutate
                # Parent A, so the offspring distribution is centered on Parent A.
                # This is a lot more like a mutation operator with a 1/ndv rate
                # than a traditional crossover operator.  But like DE, it is using
                # the population to determine an appropriate step size.
                rank_b = _select_rank(state, ramp)
                ramp += 1
                # Choose parent B from its rank.
                parent_b = _select(state, rank_b)

            # Find unequal decision variables.  (C99 allows variable-length
            # arrays.  It's a stack allocation, but it would take a _huge_
            # decision space to blow out the stack.  Still, it's a risk.
            # The alternative would be to malloc a few extra index arrays
            # into State.)
            dv_equality = [aa == bb for aa, bb in zip(parent_a, parent_b)]
            n_unequal_dvs = len(dv_equality) - sum(dv_equality)

            # Choose how many DVs to mutate
            # Here's a performance distribution based on a weak sparsity
            # of effects assumption.
            # 10% 1 variable 10
            # 20% 2 variable 30
            # 30% 3 variable 60
            # 20% 4 variable 80
            # 10% 5 variable 90
            # 5%  6 variable 95
            # 5%  7 variable 100
            draw = randint(0, 99)
            breaks = (10,30,60,80,90,95,100)

            n_dv_to_modify = 1
            for ii, limit in enumerate(breaks):
                count = ii + 1
                if n_unequal_dvs <= count or draw < limit:
                    n_dv_to_modify = count
                    break

            # Apply SBX 
            offspring = parent_a
            previous_dv = -1
            while n_dv_to_modify > 0:
                # randomly select from the unequal decision variables
                target = randint(0, n_unequal_dvs - 1)
                target_index = None
                counter = 0
                for index, isequal in enumerate(dv_equality):
                    if not isequal:
                        if counter == target:
                            target_index = index
                            break
                        counter += 1

                # Do SBX on the chosen variable, in index space.
                result = sbx_index(
                    offspring[target_index],
                    parent_b[target_index],
                    len(state.grid.axes[target_index]),
                    state.random)

                # Look up the name of the field so we can do _replace
                field = offspring._fields[target_index]
                offspring = offspring._replace(**{field: result})

                # Prepare for next iteration
                n_dv_to_modify -= 1
                # Adjust dv_equality so that we don't hit the same DV again.
                dv_equality[target_index] = True
                n_unequal_dvs -= 1

        # Treat the offspring as a direction for a line search.
        # If the offspring is not duplicated, we'll just get it back.
        offspring, duplicated = _line_search(state, parent_a, offspring)

        # Increment the "circuit breaker" so that we don't line search
        # forever in a saturated space
        circuit_breaker += 1

    # If everything failed, return a doe point
    if duplicated:
        return doe_next(state)
    return state, offspring

def sbx_index(aa, bb, allowed, random):
    """
    Perform SBX on indices.  Return a new index.

    TODO: allow to parameterize DI.

    aa (int >= 0): an index
    bb (int >= 0): an index
    allowed (int > 1): number of allowed indices
    """
    if allowed == 1:
        raise Exception("This operation will always return 0!")
    rounded_result = aa
    while rounded_result == aa:
        result = sbx(0.0, float(allowed-1), float(aa), float(bb), 1.0, random)
        difference = result - aa
        if difference > 0:
            rounded_result = aa + int(ceil(difference))
            if rounded_result >= allowed:
                rounded_result = allowed - 1
        elif difference < 0:
            rounded_result = aa + int(floor(difference))
            if rounded_result < 0:
                rounded_result = 0
    return rounded_result

def sbx(x_lower, x_upper, x_parent1, x_parent2, di, random):
    """
    Perform SBX on one variable.

    x_lower (float): lower bound on DV
    x_upper (float): upper bound on DV
    x_parent1 (float): primary parent value
    x_parent2 (float): secondary parent value
    di (float, nonnegative): distribution index
    """
    x_range = x_upper - x_lower
    gamma = di + 1.0
    kappa = 1.0 / gamma
    if x_parent1 == x_parent2:
        # early return if parents are the same
        return x_parent1
    swapped = False
    if x_parent1 < x_parent2:
        y_1 = (x_parent1 - x_lower) / x_range
        y_2 = (x_parent2 - x_lower) / x_range
    else:
        swapped = True
        y_2 = (x_parent1 - x_lower) / x_range
        y_1 = (x_parent2 - x_lower) / x_range
    delta = y_2 - y_1
    beta = 1.0 + (2.0/delta) * min(y_1, 1-y_2)
    alpha = 2.0 - beta ** (-gamma)
    uniform_1 = random()
    if uniform_1 <= 1.0 / alpha:
        beta_q = (uniform_1 * alpha) ** kappa
    else:
        beta_q = (1.0 / (2.0 - uniform_1 * alpha)) ** kappa
        # This assertion is not true! assert(beta_q <= 1.0)
    if swapped:
        sign = -1.0
    else:
        sign = 1.0
    y_child = 0.5 * ((y_1 + y_2) + sign * beta_q * delta)
    x_child = x_lower + x_range * y_child
    return x_child

def _line_search(state, parent, offspring):
    """
    state (MOEAState)
    parent (GridPoint)
    offspring (GridPoint)

    Do a line search in the parent->offspring direction

    Return a grid point and whether or not that point is duplicated.
    (grid_point, duplicated)
    """
    if not is_duplicate(state, offspring):
        return offspring, False
    # See comment in evolve() about stack allocation versus heap
    # allocation for "working" indices and flags.
    step = [o - p for o, p in zip(offspring, parent)]
    abstep = [abs(s) for s in step]
    signstep = [(int(s >= 0) * 2 - 1) * int(s != 0) for s in step]
    threshold = max(abstep)
    counters = [0 for _ in abstep]
    duplicated = True
    location = [o for o in offspring]
    search_result = offspring
    # Search further out from offspring
    failed = False
    while duplicated and not failed:
        failed = False
        for ii in range(len(counters)):
            counters[ii] += abstep[ii]
            if counters[ii] >= threshold:
                counters[ii] = counters[ii] % threshold
                location[ii] = location[ii] + signstep[ii]
                if location[ii] < 0:
                    failed = True
                elif location[ii] >= len(state.grid.axes[ii]):
                    failed = True
        search_result = state.grid.GridPoint(*location)
        duplicated = is_duplicate(state, search_result)
    if duplicated or failed:
        # Search toward parent from offspring
        location = [o for o in offspring]
        counters = [0 for _ in abstep]
        search_result = offspring
        failed = False
        duplicated = True
        while duplicated and not failed:
            failed = False
            for ii in range(len(counters)):
                counters[ii] += abstep[ii]
                if counters[ii] >= threshold:
                    counters[ii] = counters[ii] % threshold
                    location[ii] = location[ii] - signstep[ii]
                    if location[ii] < 0:
                        failed = True
                    elif location[ii] >= len(state.grid.axes[ii]):
                        failed = True
            search_result = state.grid.GridPoint(*location)
            duplicated = is_duplicate(state, search_result)

    if failed or duplicated:
        return offspring, True
    else:
        return search_result, False

def _select_rank(state, ramp):
    """
    ramp (float): Weighting ramp for relative rank probability.
                  Ramp is greater than or equal to -1.

    Returns the index of a rank to sample.
    """
    if -1.0 <= ramp:
        pass # in the domain
    else:
        raise Exception("Ramp {} is not greater than -1".format(ramp))
    occupied_ranks = 0
    for rank in state.archive:
        if rank.occupancy == 0:
            break
        occupied_ranks += 1
    # see elsewhere discussion about stack allocation
    intervals = [occupied_ranks + ramp * ii for ii in range(occupied_ranks)]
    breaks = [sum(intervals[:(ii+1)]) for ii in range(occupied_ranks)]
    limit = breaks[-1]
    selection = state.randint(0, limit)
    rank_number = 0
    while breaks[rank_number] < selection:
        rank_number += 1
    return rank_number

def _select(state, rank_number):
    """
    rank_number (index):  An index into the archive.

    Returns a GridPoint from the given rank.
    If the rank is empty, raises an Exception.
    If the rank number is outside the archive, raises
    an IndexError.  Don't do that!
    """
    rank = state.archive[rank_number]
    if rank.occupancy == 0:
        raise Exception("Can't select from an empty rank ({}).".format(rank_number))
    randint = state.randint
    target = randint(0, rank.occupancy - 1)
    counter = -1
    index = -1
    while counter < target:
        index += 1
        if rank.individuals[index].valid:
            counter += 1
        if index > len(rank.individuals):
            # Should never get here because occupancy is the number
            # of valid individuals in the rank.  If we do, it's because
            # of a bookkeeping failure somewhere else.  Probably in
            # move_individual.  Be very careful about updating the
            # contents of rank.individuals, because it's mutable!  Old
            # Ranks will be wrong about occupancy.
            raise Exception("Rank {} is inconsistent!".format(rank_number))
    return rank.individuals[index].grid_point

