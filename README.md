# δMOEA: A Multi-Objective Evolutionary Algorithm

δMOEA is a multi-objective evolutionary algorithm (MOEA),
with the following well-established algorithmic elements:

* steady-state evaluation
* uniform mutation
* simulated binary crossover
* nondomination sorting

In addition, δMOEA does some things that no other known
MOEA does:

* Uses real-valued decision variables, but produces samples
only at points on a user-specified grid.
* Retains a comprehensive Pareto-ranked archive of (almost)
every evaluated individual.
* (Almost) never suggests resampling the same grid point.
* Determines selection probability based on Pareto rank
in the comprehensive archive.

Also, δMOEA is designed for user convenience.  The key
user-friendly feature is its asynchronous evaluation model.
The default model for MOEAs is for the user to make a
single call to the MOEA, providing it with an evaluation
callback that must conform to the MOEA's expectations of
what an evaluation function does.  This rigid approach
limits the user's ability to supply extra evaluated
individuals, to establish termination conditions, and to
parallelize evaluation.  In addition, it requires
surrendering control of program execution to the MOEA.

δMOEA's asynchronous evaluation model works differently,
putting the user in control of evaluation.  Instead of one
`optimize` function, δMOEA provides two: `get_sample`
and `return_evaluated_individual`.  In between calling
these two functions, it is expected, but not required,
that the user's evaluation function will be called.
This split means that the user can:

* choose not to evaluate a particular sample
* return evaluations out of order
* return evaluations other than those suggested by the
algorithm, such as evaluations from previous optimization
runs
* call `get_sample` a different number of times than
`return_evaluated_individual`

Furthermore, although δMOEA only suggests samples on grid
points, it will accept evaluations from anywhere in the
decision space.

# Copyright

(C) 2017 DecisionVis LLC

# License

This Python implementation of δMOEA is available under
the GNU General Public License, Version 3.

# Frequently Asked Questions

## Mutation

> Why did we eliminate polynomial mutation from SBX
> crossover? In fact, it seems like we've eliminated mutation
> altogether and replaced it with continuous injection -
> is this correct?

There are two things going on here: we dropped PM and we do
"continuous injection."

### Dropping PM

To understand why we don't use PM, it's important to
understand why PM is traditionally used after SBX.  If you
configure Borg so that SBX is used by itself, performance
will suffer compared to the version with PM.  Clearly PM
is helping somehow.

The problem PM solves is that SBX scales relative to the
distance between parents.  Two parents close together in
decision space will produce offspring that's not too
different from either parent.  It's very likely that this
will happen with Borg, for a couple of reasons.  First of
all, Borg does not have any mechanism that rewards
diversity in decision space.  MOEAs generally haven't had
anything like that since sharing operators went out
of fashion.  Second, Borg's diversity maintenance only
operates on the archive.  Borg's search population has no
mechanism for diversity maintenance other than restarts.
So what happens in the experiment where you configure
Borg's SBX operator not to chain to PM is that in between
restarts the population has a tendency to stagnate very
quickly because crossover is basically interpolating
between individuals that are already close together.

δMOEA doesn't have the problem that PM solves, and
therefore PM is unnecessary for δMOEA.  δMOEA doesn't
have this problem because it uses its comprehensive
archive to ensure that it isn't generating a new sample
on an already-evaluated grid point.

### Continuous Injection

It's not really true to say that δMOEA doesn't use
mutation.  At a fixed rate, δMOEA generates a sample using
UM instead of SBX.  At the moment we have this hard-coded
to 10% of the time, although we have not explored δMOEA's
parameter space.  I suspect 10% may be too conservative,
because Borg tends to catch up to δMOEA once it starts
hitting its restart condition more often.

I've called this fixed-rate mutation "continuous injection"
because, like Borg's injection, it applies UM to its Pareto
approximation to generate new samples.  Unlike Borg,
which does injection only during a restart, δMOEA has
no notion of a restart.

## Selection

> Why proportional selection?

Calling the δMOEA selection mechanism "proportional
selection" is a little provocative.  It's a well known fact
in the MOEA community that proportional -- or
roulette-wheel -- selection fails dramatically.
Proportional selection is prone to super-solution takeover,
where because an individual has been successful, it is
rewarded with a higher selection probability, until the
entire population fills up with clones of that one
successful individual.

δMOEA doesn't do that.  The proportional selection refers
to the ranks of the comprehensive archive, not to
the individuals in the archive.  δMOEA's selection
procedure looks like this:

1. Assign a probability weighting to each rank in inverse
proportion to the rank number.  Therefore the first rank
has the highest probability, the second rank has a slightly
lower probability, and so on.
2. Select which Pareto rank to draw from based on these
weights.  This is the proportional part of the selection
procedure.
3. Randomly select one individual from within the selected
Pareto rank in the comprehensive archive.

Because δMOEA almost never emits a second sample for a
grid point that has already been evaluated, no single
individual can take over the archive.  Indeed, this is
impossible even if a user decides to return a large
number of evaluations with decision variable values that
map to the same grid point.  Even if these individuals are
nondominated with respect to each other, δMOEA's archiving
procedure only allows one individual from any grid point
in any Pareto rank.  Each near-duplicate would be forced
into a lower rank in the archive.

## Crossover

### Changes to SBX

> What changes have been made to SBX crossover and why?
 
There have been three changes to SBX:

1. SBX in δMOEA produces offspring only at grid points.
2. SBX in δMOEA produces one offspring rather than two.
3. SBX in δMOEA does not treat the two parents
symmetrically.

#### Offspring at Grid Points

Producing offspring only at grid points is accomplished
by rounding the results of SBX to the nearest grid point.

#### One Offspring at a Time

The original argument for producing two offspring is that
doing so avoids biasing the search towards either parent.
This is a weak argument because ordinarily both parents
have equal probability of selection.  Furthermore it might
be desirable to bias the search towards one parent rather
than the other.

#### Biasing the Search Towards One Parent

Proportional selection by rank is used only for the second
parent in SBX.  The first parent is always selected at
random from the first Pareto rank.  (As is the parent when
applying UM for continuous injection.)  The SBX procedure
used by δMOEA is biased towards the first parent, because
it is guaranteed to come from the first Pareto rank.  The
second parent is used to provide a direction in which to
modify the first parent to produce a new sample.

SBX ordinarily uses a hidden parameter: any variable has a
50% chance of being subjected to SBX.  If it is not, its
value is inherited unchanged.  Besides a vague mention of
schema processing in the paper introducing SBX, there is no
argument in favor of this rate anywhere in the literature.
50% may have been an appealing rate based on analogies to
real-world genetics.

δMOEA achieves its bias towards the first parent
by lowering this rate parameter.  Based on a moderate
sparsity-of-effects assumption, δMOEA never applies SBX
to more than 7 variables, and is most likely to apply
SBX to 2, 3, or 4 variables.  Because it applies SBX at a
lower rate, δMOEA produces offspring that most strongly
resemble the parent from the first Pareto rank.  (δMOEA
uses the same approach when applying UM, rather than using
a rate of 1/ndv.)

### Rotationally Invariant Search Operators

> Why is the argument for rotationally invariant operators
> over-rated, particularly in the context of SBX (which
> is not rotationally invariant) usually performing very
> well?

Rotational invariance isn't really a well-defined concept
when it comes to crossover operators.  It's based on
a contrast between the rectangular appearance of the
offspring distribution for SBX in a two-dimensional
plot, compared with the more blob-like appearance of the
offspring distribution for other operators.  This
appearance is partly the result of the hidden 50% rate
parameter in SBX, and partly the result of the tendency of
SBX to favor solutions close to one parent or the other,
although the latter tendency varies with the chosen
distribution index.  Furthermore, because PM is
conventionally applied at a rate of 1/ndv, the offspring
are further spread along the axes in a two-dimensional,
two-decision plot.

There is a much more interesting, important difference
between SBX and the other search operators.  Primarily, SBX
uses only two parents.  SPX, PCX, and UNDX default to 10.
While they all employ rather complicated mathematics, these
operators boil down to producing averages on the parents.
We could just as well produce averaging results using
SBX if we increased its hidden rate parameter to 100%.
This is also the reason that SBX always performs better
than other operators early in a Borg run: taking the
average of ten mediocre solutions is going to produce
mediocre results.  It's only late in the run, when the
search has largely converged, that Borg finds any advantage
in averaging large numbers of parents.

## Saturation

> Lake is concerned about ranks filling up and
> non-dominated solutions being pushed to inferior ranks.

This definitely degrades algorithmic performance.  It's
easily detected -- I could put in a warning -- and easy
to mitigate.  The reason it showed up so prominently in the
diagnostic runs we did is that the diagnostic runs were
designed to provoke saturation of the first Pareto rank.

The manual way to mitigate saturation is to halt the
algorithm when the first rank fills up, export the archive,
and then feed it back into a new instance of δMOEA
initialized with larger archive ranks.  Also, saturation
can be avoided entirely with some advance knowledge
about the problem and the intended run.  A run of 30,000
evaluations will never have more than 30,000 individuals in
the first rank of the archive, for example.  Assuming we
need 1000 64-bit floating-point numbers to represent an
individual (which is a very generous number!) we could
size the archive to 100 ranks of 30,000 individuals at
a cost of 8Gb of memory.  If this seems like a lot, the
workstation on which this is being typed is currently
using that much memory to run a web browser.

If prevention and manual intervention are inadequate, we
can address saturation through algorithmic means, by
automatically repartitioning the memory allocation that
backs the archive into fewer, larger ranks.

## Performance

> How do the wall-clock times of δMOEA runs compare to
> Borg MOEA? (A question we should answer after we have the
> C implementation in place).

The major performance concern with δMOEA is the overhead of
scanning the comprehensive archive every time it emits a
new sample, sometimes many times.  This has not been an
issue for the Python implementation of δMOEA because it
uses a hash set for fast membership checks.  Hashing is a
well established technique for accelerating lookups, and if
we find that archive scans are too slow, we can replace
them with hashing.  As with the saturation issue, we'd like
to avoid complicating the algorithm until we're sure it's a
problem.

