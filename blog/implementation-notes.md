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
