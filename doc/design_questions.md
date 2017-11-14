# δMOEA Questions and Answers

Matthew Woodruff

2017-11-13

# Number of Mutated Variables

> Is there a reasoning for the hard-coded probabilities
> for changing 1 to 7 decision variables in the continuous
> injection process? Or could this be parameterized similar
> to the 10% probability of doing the continuous injection
> vs. crossover?

These were chosen according to a sparsity-of-effects
heuristic.  The idea is that we want to minimize the
effect of interactions when doing mutation.  Sparsity of
effects isn't a law of probability, but an observational
generalization that says the probability of interaction
usually declines with the number of variables involved,
and that interaction effects are usually weaker than
first-order effects.

This line of reasoning leads us to assume that the
probability that any set of three variables will contain
an interaction is reasonably low.  That's why I set up
a probability distribution that peaks at three mutated
variables.  It ranges between one and seven because, on the
one hand, we can accept some amount of interaction when it
helps us explore the problem space more thoroughly, and on
the other hand, we'd like for there to be some probability
of making extremely conservative mutations in case the
problem violates the sparsity of effects assumption.

Unfortunately, this is unsubstantiated hand-waving.
A theme I'm going to return to in this response is
that there are lots of parameter-tuning experiments we
could do, and because of time constraints I've done none
of them.  For this particular heuristic, the main things
to investigate are:

1. Should the number of mutated variables vary in a fixed
range as it does now, or should it vary in proportion to
the overall number of decisions?
2. Is the distribution on the number of mutated variables
too aggressive or too conservative, in general?
3. Is the 10% continuous injection rate too low or
too high?  I suspect it's too low, and this is the first
question I would investigate given the resources to do so.

The short answer is that, while there are reasons for
the choices I made, you are free, and indeed encouraged,
to tweak this heuristic.

# Random Solution Generation

> My understanding is that only the initial population is
> randomly generated. After that, the mutation of select
> decision variables or crossover is performed to generate
> new chromosomes, except in the case that crossover and
> mutation fail for 10 consecutive loops of attempting to
> evolve to a non-duplicate chromosome. Is this understanding
> correct?

This is approximately correct.  There's a twist, in that
the DOE generating the initial population doesn't have
to be RANDOM, although that is its default.  The DOE is a
"design of experiments."  It progresses as:

`CORNERS -> OFAT -> CENTERPOINT -> RANDOM -> EXHAUSTIVE`

For the most part, `CORNERS` and `OFAT` are too
computationally expensive, but if you have a very
small number of decisions you might want to try them.
(Another thing they do is find good ways to break your
model.)  Initial sampling terminates on a specified DOE
stage transition, or if a specified number (`COUNT`)
of samples has been issued.

If you subsequently draw too many duplicates during
evolutionary sampling, δMOEA will fall back on the next
DOE sample.  If your current DOE stage is `RANDOM`, then
you get a random point.  If it's `EXHAUSTIVE` then the
exhaustive sampling counters tick up by one and you get
the next unsampled point.  If it's `OFAT` then you get the
center of one of the faces of the decision space hypercube.
And so on.

Short answer: yes, if you stick to the defaults, we fall
back to a random point.

# Loop Limits in Sampling

> Similar to question 1, the hard-coded loop limits could
> be parameterized?

Many of the hard coded loop limits are driven by the
structure of the problem.  Most of our loops are looping
over the decision variables, so there aren't any other
options that make sense.  There are some exceptions though:

## Transition to Exhaustive Sampling

1000 duplicates triggers the transition from `RANDOM` to
`EXHAUSTIVE` sampling.  If you have a really long function
evaluation, it might be worth trying harder to get a new
random sample.

## Selection Ramp

This is the probability ramp in `select_rank`.  Right now
the ramp is steeper if you have a small number of occupied
ranks, and there's always some probability of sampling any
occupied rank.  There are a couple of things you could do
with this:

* Use a fixed ramp, so that some ranks will never
get sampled.
* Use a nonlinear or piecewise function of rank,
so that the first few ranks are highly probable and
there's a steep decline afterwards.

However, I'd caution against trying to get too clever
with this one.  Not only is the logic fiddly, but more
importantly the payoff is low.  We've seen historically
that elitism works well.  That's why we always draw one
crossover parent from Rank 0.  Since δMOEA makes it very
hard to produce duplicate samples in general, and in
particular from the most dominant ranks, it's unlikely
that "super-solutions" will take over as a result of
this strategy.  Furthermore, continuous injection is
constantly stirring the pot and introducing new genetic
material.  If you want to tweak the exploration versus
exploitation balance, I highly recommend doing so by upping
the continuous injection rate instead of adjusting the
selection ramp.

## Random Sample After 10 Duplicates

In densely sampled parts of the decision space, we're
likely to hit duplicates.  You could move the needle on
exploration versus exploitation by lowering this number,
but random individuals are *really* random and you're
unlikely to get very good genetic material with a shot in
the dark.

# Constraint Handling

> `dmoea_constraint` has a “sense”, similar to `dmoea_objective`:
>
> ```
> struct dmoea_objective {
>     char *name;
>     enum dmoea_objective_sense sense;
> };
> struct dmoea_constraint {
>     char *name;
>     enum dmoea_objective_sense sense;
> };
> struct dmoea_objective objectives[NOBJ] = {
>     {"objective0", MINIMIZE},
>     {"objective1", MINIMIZE}};
> struct dmoea_constraint constraints[NCONSTR] = {
>     {"constraint0", MINIMIZE},
>     {"constraint1", MINIMIZE}};
>
> ```
>
> Is dmoea driving constraints to feasibility? Given our
> “normal” constraints with larger negative number being
> worse, should we, by default, set the dmoea_constraint
> to MAXIMIZE?

The role of constraints in δMOEA is to determine how
individuals are ranked into the archive.  They take priority
over objectives, which only affect sorting for feasible
individuals.

The crucial number for δMOEA constraints is zero.
A `MINIMIZE` constraint is satisfied when its value is
less than or equal to zero.  A `MAXIMIZE` constraint is
satisfied when its value is greater than or equal to zero.
It sounds like you want `MAXIMIZE` constraints, if more
negative is worse.

# Pseudo-Random Number Generation

> What was the reasoning behind the choice of random number
> generator? Are you knowledgeable on the sensitivity of
> a GA’s performance in relation to the choice of random
> number generator?

I used the Mersenne Twister, which is well-regarded for
non-cryptographic applications.  `random(3)` should be OK
according to my reading of the man page.  Just don't use
`rand(3)`.

I don't have any specific knowledge when it comes to
the effect of the PRNG on optimization performance, but
in general we assume that random number generators are
free of bias, and the POSIX standard doesn't make many
guarantees about `rand(3)`.
