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
    DOE state.  If there aren't enough solutions in the
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
