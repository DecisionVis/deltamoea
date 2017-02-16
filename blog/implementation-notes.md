# Implementation Notes

This is going to be a non-adaptive multi-operator search.  Like I've
said, I'm skeptical about auto-adaption and "rotated" search
operators.  Instead I'm going to break things down and have SBX, a
low-DI (big steps) PM, and a high-DI (little steps, but high
probability) PM.  Actually, maybe the same thing with SBX, have two
SBX, one with big steps and low probability and one with little
steps and high probability.


## PM (inner)

I've modified the formula a bit. I really don't understand why
they've needlessly complicated it.  It makes me doubt that they knew
what they were doing.  Either that or it's kind of a watermark to
see whether people have been copying their code.

Anyhow, my gamma is the same as (1-delta) in the formula, since
that's all they use.

Also my "beta" is the second term in braces, which is actually the
same in both versions and hides a subtraction.

And my "alpha" is η+1, again since that's all they use.

The "exponand" is everything in brackets.

# Taking Stock

2017-02-12

So there are now two different starts at this, each with its own
advantages.  The first try, the current `moeadv.py`, is more
Pythonic, does a lot of dynamic allocation, and locks up when
you try to generate a child in a densely sampled region.

The second try (`second_try.py`, creatively named such) isn't
an algorithm yet at all, just a bunch of ideas.  But some of them
are much better ideas than in `moeadv.py`, especially from
the point of view of eventual C-ification.  Also I have a pretty
strong idea of how to do the DOE at this point.

The question I want to ask myself now is, can I outline the
data structures and algorithm at this point?

# Data Structures

## Decisions, Objectives, Constraints

The basics.  Everything is assumed to be continuous
(float 64).  Naturally some integer variables will
exist.  Specifying an appropriate delta will tell
the MOEA not to waste time sampling in between zero
and one.  Nevertheless, we will accept some loss of
efficiency in the conversion back and forth, to
simplify the representation.

## Tagalongs

Lest we forget.

## Individual

A struct

Decisions + ndecisions
Objectives + nobjectives
Consntraints + nconstraints
Tagalongs + ntagalongs

## The Popularchive

This is my tiered, preallocated, huge population.  It could
be one big preallocation, with the step between ranks as a
parameter.  Needs an invalid flag column.

## Popularchive metadata

Occupancy count for each tier so we know where to stop when
searching or sorting.

## The Grid

This is the axes of the grid, not the whole mesh.

## DOE state

A counter and an enum (center, faces, corners, unirand).
A 64-bit unsigned counter is adequate for the corners even
though it's possible we'll never run out of corners, because
we're going to run out of memory first anyway.

## An array of comparators

For the objective functions and constraints.

# Functions

## Coordinate Conversion

Index to decision space and decision space to index.

## Allocate State Structure

Arguments: definition of an Individual
Returns: pointer to a state structure

## Return Evaluated Individual

Arguments:
    * pointer to an individual
    * MOEA state structure
Returns:
    * MOEA state structure

## 

# Top-Down View

As a library user, I:

1.  Define Decisions, Objectives, Constraints, Tagalongs
2.  Tell the library to allocate me an MOEA state structure.
    This is a huge thing, containing the Popularchive and
    everything else listed above.
3.  At my option, call return_evaluated_individual, which
    puts evaluated individuals into the MOEAstate.
4.  At my option, call state_doe to force the MOEA into a
    DOE state.  If there aren't enough individuals in the
    popularchive, I understand that the MOEA will transition
    into a DOE state anyway.
5.  Enter main loop.
    1. Call next_sample to get a new individual to evaluate
    2. Evaluate the individual.
    3. Do whatever I want.  Print stuff to the screen, operate
       a GUI frontend, do local optimization on the
       individual, generate seven other individuals along
       with the one I just evaluated, or whatever.
    4. Call return_evaluated_individual some number of times.
       Could be zero if I'm just not feeling it.
6.  Call get_rank(0) to get the archive and save it somewhere.
    Or get_rank(i) to get a later rank and save it somewhere
    too.
    
# C Interface

```
state* setup(error* e, problem* p, options* o)
void teardown(state* s, error* e)
state* return_evaluated_individual(state* s, error* e, individual* i)
state* get_sample(state* s, error* e, double* d)
state* doe(state* s, error* e) // request DOE samples
void get_iterator(state* s, error* e, individual_iterator* it, rank r)
void iterator_next(state* s, error* e, individual_iterator* it, individual* i)
```

That's it in a nutshell.  Any function that changes state,
returns a state pointer.  Every function produces an
error code and writes it back to the provided pointer.
You can choose to ignore the error code, but you have
to recon with it every single time you call a function.
We will not guarantee that state pointers never change.
Furthermore, old state pointers should be assumed to become
invalid after any state transition.  We handle multiple
return in the traditional C fashion -- with pointers.

When you use this, you can allocate pretty much everything
on the stack.  Your problem, your decisions and objectives,
your individual, your error code, your iterator.  What you
can't allocate on the stack is MOEA state.  That gets 
allocated by the setup function.  After that it's your 
responsibility to clean up the MOEA state by calling the
teardown function.  There is no other resource management
by the library user.

# Top Down Python Version

2017-02-13 11:45

Last night, I wrote my "top-down" version, a template
algorithm run that exercises the whole API I outlined
above.  My next step is to implement the next layer
down.  Some of the next layer down already exists but
isn't hooked up to the top-down template yet.

So, what's missing?

* decision, objective, constraint, tagalong
* Problem
* create_moea_state (this is a big one)
* return_evaluated_individual
* get_iterator
* (iterator as generator)
* teardown

# What About Evaluated Individuals With Non-Grid Decisions?

It's entirely possible to return an individual with
decisions that don't fall on the grid.  What do we do
with those?

First of all, we'll stipulate that it's up to the users
to provide on-grid individuals if that's what they want.

We're going to interpret off-grid individuals as if they
were at the grid point.  Furthermore, we're going to
discard the decision variable values and convert them
to indices.  It's important that the user recognizes this.
If the original values of the decisions are important,
they must be preserved in tagalongs.

## Why This Might Happen

There are a few circumstances that might lead up to
a situation like this.

One is a change in sampling resolution.  The user decides
to increase or decrease sampling resolution and restart
the MOEA, reusing the old samples.  Unless using an integer
multiple of the original resolution, the old samples
won't fall on the new grid.

Another is reuse of external model runs that were done for
other reasons.  These may have been guess-and-check scenarios,
or evalutations from DACE or Kriging runs, or what have you.
The user has the results on hand and wants to use them, and
we want to take advantage of that.

The third circumstance I can think of is the insertion of
a local optimizer as a post-evaluation fixup.

In all of these cases it's important for the user to plan
ahead and preserve the off-grid decision variable values
as tagalongs, because they will be lost otherwise.

## Pathological Cases

The worst case scenario is downsampling.  In this case
we have multiple individuals for each grid point.  So even
though we take care never to generate duplicate samples,
we have to accept that the user might have perfectly
legitimate reasons to supply off-grid individuals.

## Strategy

My strategy for off-grid individuals is to keep all of
them, subject to archive size constraints.  However, they
can't be allowed to compete with the on-grid individuals
as if they were equivalent.  I'm still working on how to
make that happen.

### Change of Heart

Why not?  New strategy: every individual gets to participate
in the sort.  We're not going to resample already-sampled
grid points anyway.

### Retention

An option flag should be provided for retaining decision
variables.  Default behavior will be to discard real values
and retain only grid points.

# Issued Samples

We should also allocate a list of issued samples for which
we do not yet have an evaluated individual.  It should probably
have ranksize members or so.

# Preemption

2017-02-16 12:19

It would be really easy to add multiple levels of preemption to 
my sorting procedure.  All you would have to do would be to
take the current sorting procedure and put an extra for loop
around the constraints.

Presenting this to the user is the hardest part.
One approach would be for constraints to be defined in parallel with
levels of preemption.  We could call the levels of preemption
"goals" or perhaps "goal levels".  The way things would work in
this account is that the constraints are really the zeroth
level of preemption.  And then the "goals" are the first through
nth levels of preemption.  Finally the objectives are what they've
always been, with no saturation.

# Selection and Variation

2017-02-16 12:34

I'm going to present a more detailed account of selection
and variation operators now, since the time has come to
implement them.

## What Do We Want To Produce?

Selection and variation have a different role in UDMOEA
than in MOEAs in general.  MOEAs in general want to
find a well-spaced Pareto front in objective space,
and they're willing to make a trifling nudge in decision
space to do so.  UDMOEA on the other hand wants to find
a well-spaced Pareto front in decision space.  That means
we must make a minimum of a one-delta step.

Given a set of nondomination ranks and a list of issued
samples, we want to produce a sample at a grid point that
is not in any of those.  Furthermore, we would like that
grid point to have a good chance of advancing the search.
If it weren't for the second requirement, we could just
have a policy of always selecting points adjacent to the
archive.  But this is what variation operators buy us.
In particular, SBX does this for us, because it chooses
a step size based on two "good" individuals.

## Why Do We Usually Combine SBX with PM?

The advantage of PM over SBX is that it makes steps scaled
to the decision space rather than to the parents.  This
helps introduce genotypic variation when your population
has started to converge towards a point.  Needless to
say, that's not as much of an advantage here.  I'm leaning
strongly towards excluding PM from the algorithm.

## In What Direction Should We Step?

Conventional MOEAs step in more than one direction at a
time.  Every SBX implementation I've seen (Borg, Platypus,
JMetal, NSGAII classic, Shark) applies SBX to every
variable (with a probability of 50%).  This is a hidden
parameter that goes without question.  I haven't seen
any justification in the literature for this, and it seems
dramatically at odds with common sense.  (And this is not
to mention the odd feature that SBX always gives birth to
twins.)  The common sense I refer to is the "sparsity of
effects principle," known to statisticians as a rule of
thumb.  It's not an iron law, but in general it states
that interactions in physical systems are weaker than
first-order effects, and that the higher the order of the
interactions, the weaker they are.

Therefore, instead of the 50% rule, which makes, to coin
a phrase, a "density of effects" assumption, let's do
a 90-10 rule: 90% of the time, we do SBX on a single variable.
10% of the time we choose 2 variables.

Furthermore, we will treat the parents asymmetrically.
The offspring will be based on the left parent, but SBX
will produce a distribution around the right parent's
grid point for the chosen variables.

## Which Brings Us Back To Selection

So where are the parents from?  Yesterday I was saying
they should be selected propotionally from the archive
ranks without regard to the occupancy of those ranks.
But then I started worrying about pathological cases,
where the ranks are really small.  This leads me to a
suggestion that actually brings us almost all the way back
to classic proportional selection: weight the probability
of choosing each rank by its occupancy.  Don't let the
last rank participate because it's a dumping ground for
dominated individuals.

Actually, we need different probabilities for the two
parents.  The first parent should be chosen from rank 0
with probability 1.  (Remember that we get our diversity
guarantee from the decision grid.)  Then the second parent
gets chosen with some probability that's possibly modulated
by occupancy.

Brainstorming a procedure:

1. Start by assigning an un-normalized probability to each
   rank, equal to the occupancy of that rank.  Exclude the
   last rank.
2. Divide each rank's probability by (1+rank number).  Or
   multiply by 2 ** (-rank number).  Or some other function
   that makes probability decline.
3. Normalize the probabilities.

The problem with this is that it seems very sensitive
to parameterization.

What I actually want is for the second parent to have a
high probability of coming from rank 0 if rank 0 is big,
with that probability declining as rank 0 gets smaller.
The problem is defining what "big" means.  One way of
looking at this is by defining thresholds.

Maybe we just want one parameter.  A population size
perhaps?  (Trolling myself a little here.)  This parameter
is how many individuals get to participate in selection.

Suppose we just always selected the second parent from
Rank0.  How does this get us in trouble?  If Rank0
is small, it inhbits diversity.  The point is that
slightly-dominated individuals may still be quite good.
Take the worst-case scenario, where we have a single
objective and ranks of a single individual.
