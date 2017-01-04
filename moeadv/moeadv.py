from collections import namedtuple
from array import array
from moeadv.operators import sbx_inner
from moeadv.operators import pm_inner
import random

_EMPTY_TUPLE = tuple()

# Decision: name(string) lower(float) upper(float) delta(float < upper - lower)
Decision = namedtuple("Decision", ("name", "lower", "upper", "delta"))
# Objective: name(string) sense("min" or "max")
Objective = namedtuple("Objective", ("name", "sense"))
# Constraint: name(string) sense("min" or "max")
# Constraints are special because they are always relative to 0.
# A "min" constraint is met if <= 0
# A "max" constraint is met if >= 0
Constraint = namedtuple("Constraint", ("name", "sense"))

class RandomUniform(object):
    def __init__(self, decisions):
        self._decisions = tuple(decisions)
        self._ranges = dict(((d, d.upper - d.lower) for d in self._decisions))

    def next_sample(self):
        """
        uniform random sampling for now
        """
        return [random.random() * self._ranges[d] + d.lower
                for d in self._decisions]

def obj_dominance(objectives):
    """ return a dominance comparison for the given objectives """
    def less(a, b): return a < b
    def greater(a, b): return a > b
    comparators = list()
    for objective in objectives:
        if objective.sense == "min":
            comparators.append(less)
        else:
            comparators.append(greater)
    def _dominance(left, right):
        """
        left (list of float): "left" objectives
        right (list of float): "right" objectives
        Return "left" if left dominates, "right" if right dominates,
        or "non" if neither dominates.
        """
        a_dominates = True
        b_dominates = True
        for comparator, aa, bb in zip(comparators, left, right):
            if b_dominates and comparator(aa, bb):
                b_dominates = False
                if not a_dominates:
                    break
            elif a_dominates and comparator(bb, aa):
                a_dominates = False
                if not b_dominates:
                    break
        if a_dominates and not b_dominates:
            return "left"
        elif b_dominates and not a_dominates:
            return "right"
        return "non"
    return _dominance

def con_dominance(constraints):
    signs = list()
    for constraint in constraints:
        if constraint.sense == "min":
            sign = 1
        else:
            sign = -1
        signs.append(sign)
    def flatten(con):
        flattened = [x for x in con]
        for ii, (ss, xx) in enumerate(zip(signs, con)):
            if ss * xx < 0:
                flattened[ii] = 0
        return flattened
    dom = obj_dominance(constraints)
    def _dominance(left, right):
        left = flatten(left)
        right = flatten(right)
        return dom(left, right)
    return _dominance

class MOEA(object):
    def __init__(self, decisions, objectives, constraints, **kwargs):
        """
        decisions (iterable of Decision): decision variables
        objectives (iterable of Objective): objectives
        constraints (iterable of Constraint): constraints
        """
        self.decisions = tuple(decisions)
        self.objectives = tuple(objectives)
        self.constraints = tuple(constraints)

        DOE = kwargs.get("DOE", RandomUniform)

        # samples: a dictionary to hold every sample
        # keys: tuple of integer-ized decisions
        self.samples = dict()

        # population: a list of sample indices
        self.population = list()
        # archive: a list of sample indices
        self.archive = list()

        # state can be "evolving", "DOE", or "injecting"
        self.state = "evolving"

        # DOE-related state
        self._remaining_doe_samples = 0
        self._doe_sampler = DOE(self.decisions)

        # injection-related state
        self._remaining_injection_samples = 0

        # evolution operators
        self._pm = [pm_inner(d.lower, d.upper, 50) for d in self.decisions]
        self._sbx = [sbx_inner(d.lower, d.upper, 15) for d in self.decisions]

        self._obj_dominance = obj_dominance(self.objectives)
        self._con_dominance = con_dominance(self.constraints)

        # this is a publicly readable
        self._evolution_count = 0

    def population_rows(self):
        """ generator, produces rows corresponding to population members """
        for index in self.population:
            assert(all(type(i) is int for i in index))
            decisions = self._index_to_decisions(index)
            assert(all(type(x) is float for x in decisions))
            objectives, constraints = self.samples[index]
            yield(decisions + objectives + constraints)

    def archive_rows(self):
        """ generator, produces rows corresponding to archive members """
        for index in self.archive:
            assert(all(type(i) is int for i in index))
            decisions = self._index_to_decisions(index)
            assert(all(type(x) is float for x in decisions))
            objectives, constraints = self.samples[index]
            yield(list(decisions) + list(objectives) + list(constraints))

    def doe(self, nsamples):
        """
        State change: clear population and generate initial_population_size
        DOE samples.
        """
        self.population = list()
        self.state = "DOE"
        self._remaining_doe_samples = nsamples

    def inject(self, pop_to_archive):
        """
        pop_to_archive (float > 0): ratio of population size to archive size
        for injection.  If less than 1, no injection will happen and the
        population will be trimmed to a randomly sampled subset of the archive.
        """
        self.population = list()
        desired_pop_size = int(pop_to_archive * len(self.archive))
        if desired_pop_size >= len(self.archive):
            for index in self.archive:
                self.population.append(index)
            self._remaining_injection_samples = desired_pop_size - len(self.population)
        else:
            consumable_copy = [index for index in self.archive]
            while len(self.population) < desired_pop_size:
                jj = random.randint(0, len(consumable_copy) - 1)
                index = consumable_copy.pop(jj)
                self.population.append(index)
            self._remaining_injection_samples = 0
        self.state = "injecting"

    def _state_transition(self):
        if self.state == "DOE":
            if self._remaining_doe_samples <= 0:
                self.state = "evolving"
        if self.state == "injecting":
            if self._remaining_injection_samples <= 0:
                self.state = "evolving"
        assert(self.state in ("DOE", "injecting", "evolving"))

    def _decisions_to_index(self, decisions):
        assert(all(type(x) is float for x in decisions))
        return tuple(
            int((x - d.lower) / d.delta)
            for x, d in zip(decisions, self.decisions))

    def _index_to_decisions(self, index):
        assert(all(type(i) is int for i in index))
        return tuple(
            (i + 0.5) * d.delta + d.lower
            for i, d in zip(index, self.decisions))

    def _decisions_in_history(self, decisions):
        assert(all(type(x) is float for x in decisions))
        index = self._decisions_to_index(decisions)
        assert(all(type(i) is int for i in index))
        return index in self.samples

    def _produce_offspring(self, parent_1, parent_2):
        """
        parent_1 (list of float): decision variable values
        parent_2 (list of float): decision variable values
        """
        offspring = [x for x in parent_1]
        sbx_variable = random.randint(0, len(self.decisions) - 1)
        sbx = self._sbx[sbx_variable]
        x1 = parent_1[sbx_variable]
        x2 = parent_2[sbx_variable]
        o1 = sbx(x1, x2)
        offspring[sbx_variable] = o1

        if len(self.decisions) == 1:
            return offspring
        pm_variable = sbx_variable
        while pm_variable == sbx_variable:
            pm_variable = random.randint(0, len(self.decisions) - 1)
        pm = self._pm[pm_variable]
        offspring[pm_variable] = pm(offspring[pm_variable])
        return offspring

    def _select(self, count):
        popsize = len(self.population)
        selected_indices = list()
        if count >= popsize:
            for counter in range(count):
                selected_indices.append(self.population[counter % popsize])
        else:
            for _ in range(count):
                option_a = self.population[random.randint(0, popsize - 1)]
                option_b = self.population[random.randint(0, popsize - 1)]
                assert(all(type(i) is int for i in option_a))
                assert(all(type(i) is int for i in option_b))
                obj_a, con_a = self.samples[option_a]
                obj_b, con_b = self.samples[option_b]
                # binary tournament selection
                if self._con_dominance(con_a, con_b) == "left":
                    selected_indices.append(option_a)
                elif self._obj_dominance(obj_a, obj_b) != "right":
                    selected_indices.append(option_a)
                else:
                    selected_indices.append(option_b)
        selected_decisions = [
            self._index_to_decisions(i) for i in selected_indices]
        return selected_decisions

    def _evolve(self):
        popsize = len(self.population)
        # this shouldn't happen, but if it does fall back on the DOE
        if popsize < 2:
            decisions = self._doe_sampler.next_sample()
            while self._decisions_in_history(decisions):
                decisions = self._doe_sampler.next_sample()
            return decisions
        parent_1, parent_2 = self._select(2)
        decisions = self._produce_offspring(parent_1, parent_2)
        return decisions

    def _injection_sample(self):
        parent_index = self.archive[
            self._remaining_injection_samples % len(self.archive)]
        parent = self._index_to_decisions(parent_index)
        offspring = [x for x in parent]
        pm_variable = random.randint(0, len(self.decisions) - 1)
        pm = self._pm[pm_variable]
        offspring[pm_variable] = pm(parent[pm_variable])
        return offspring

    def generate_sample(self):
        self._state_transition()
        if self.state == "DOE":
            self._remaining_doe_samples -= 1
            decisions = self._doe_sampler.next_sample()
            while self._decisions_in_history(decisions):
                decisions = self._doe_sampler.next_sample()
        elif self.state == "injecting":
            self._remaining_injection_samples -= 1
            decisions = self._injection_sample()
            while self._decisions_in_history(decisions):
                decisions = self._injection_sample()
        else:
            decisions = self._evolve()
            while self._decisions_in_history(decisions):
                decisions = self._evolve()
            self._evolution_count += 1
        # align the decisions
        return self._index_to_decisions(self._decisions_to_index(decisions))

    def _sort_into(self, index, population_or_archive):
        obj, con = self.samples[index]
        kick_out = list()
        disqualified = False
        for ii, current in enumerate(population_or_archive):
            cur_obj, cur_con = self.samples[current]
            cd = self._con_dominance(con, cur_con)
            if cd == "right":
                disqualified = True
                break
            elif cd == "left":
                kick_out.append(ii)
                continue
            od = self._obj_dominance(obj, cur_obj)
            if od == "right":
                disqualified = True
                break
            elif od  == "left":
                kick_out.append(ii)
                continue
        if disqualified:
            return False
        while len(kick_out) > 0:
            population_or_archive.pop(kick_out.pop())
        population_or_archive.append(index)
        return True

    def receive_evaluated_sample(self, dec, obj, constr=_EMPTY_TUPLE):
        index = self._decisions_to_index(dec)
        self.samples[index] = (obj, constr)
        # sort into the population / archive
        if self._sort_into(index, self.population):
            self._sort_into(index, self.archive)

    def evolution_count(self):
        return self._evolution_count

"""
Triggering an initial sample and triggering a restart will both
be done "manually" by the user.  This means that the restarting
strategy is up to the user.  We will provide template code that
does restarts on a fixed schedule.

The reason these are not baked into the MOEA is that we want to
give the user flexibility to continue a previous run, return
multiple evaluations for each sample, discard evaluations, and
so on.  We're providing the mechanism along with sensible defaults
and example code, and they get to use or modify it however they
want.
"""
'''
class MOEA(object):

    def __init__(self):
        self.state = "evolving"


    def doe(self):
        """
        Effect a transition to the "DOE" sampling state.
        Clear the population and generate new samples based on a
        statistical design of experiments.
        After a certain number of samples are generated, return to the
        "evolving" state.

        You're most likely to use this when doing an initial sample.
        This will probably use something like LHS.
        """
        self.state = "DOE"
        # also set doe sample size

    def inject(self):
        """


    def generate_sample(self):
        if self.state == "DOE":
            child = self.doe_sample()
            self.doe_samples += 1
            if self.doe_samples - self.previous_doe_samples >= self.doe_sample_size:
                self.state = "evolving"
                self.previous_doe_samples = self.doe_samples
        elif self.state == "injecting":
            child = self.injection_sample()
            self.injection_samples += 1
            if self.injection_samples - self.previous_injection_samples >= self.injection_sample_size:
                self.state = "evolving"
                self.previous_injection_samples = self.injection_samples
        else:
            parent_1 = self.selection()
            parent_2 = self.selection()
            child = parent_1
            if random_number < 0.9: #sparsity of effects
                variable = random_choice(self.variables)
                operator_chain = self.sparsity_operator_chain()
                left_parent = parent_1
                for operator in operator_chain:
                    child = operator((left_parent, parent_2), (variable,))
                    left_parent = child
            else:
                variables = (
                    random_choice(self.variables), random_choice(self.variables))
                operator_chain = self.interaction_operator_chain()
            # There is no option here for high order interaction.  It's a tradeoff,
            # but I'd rather focus on first and second order effects, in that order.
            # Picking the right higher-order interaction is so unlikely, and then
            # picking the right direction is even unlikelier, it's something I'd
            # prefer we did as part of injection instead.
        return child

    def injeciton_sample(self):
        # why apply UM here?  Why not PM with a small DI?

    def sparsity_operator_chain(self):
        operator_chain = list()
        # flip a coin and decide whether to do SBX
        # if not SBX, definitely PM
        # if SBX, maybe PM
        # regardless, the DIs are intermediate: 10-20
        return operator_chain

    def interaction_operator_chain(self):
        operator_chain =list()
        # flip a coin and decide whether to do SBX
        # if not SBX, definitely PM
        # if SBX, maybe PM
        # Here the DIs should be pretty high, more like 30 for SBX
        # and 100 for PM
        return operator_chain

    def receive_evaluated_sample(self, sample):
        nondom = self.sort_into_population(sample)
        if nondom:
            self.sort_into_archive(sample)
'''
