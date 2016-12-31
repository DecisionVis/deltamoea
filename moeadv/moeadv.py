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
