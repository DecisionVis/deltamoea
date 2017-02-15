# Marginalia

This is a file of stray notes that deviate from whatever point I'm
trying to make in a blog post.


## Auto-Adaptation of Parameters is Dangerous

2016-12-18

Not only dangerous, but quite possibly counterproductive and prone
to getting oneself into local minima.  Now, Borg has
auto-adaptation, but note that it's not auto-adapting its search
operator parameters.  Here are the adaptive things Borg does:

* Operator selection.  But I think this is as much a signal
  indicating convergence as it is a technique that makes real
  progress possible.  I.e. by the time you switch from SBX+PM to
  another operator, you've probably already reached a point where
  you're not making big gains.  Furthermore, I think my notional
  δMOEA will require different search operators anyway.
  Note that this idea is not unique to Borg and goes back at least
  to AMALGAM or μGA^2, whichever came first.
* Tournament sizing.  This auto-adapts to population size.  Which is
  a good idea because it cranks up the selection pressure as the pop
  size increases.  I think this is a pretty marginal improvement
  however.  The population size seems to be pretty well determined
  by epsilons and injection rate anyhow.  I mean, we could do some
  experiments, but I don't think n-ary tournaments are a big win.
  Also, here's another parameter we left out of the sensitivity
  study.  Again, Borg is only insensitive to the parameters that
  don't matter.  Not to mention, this is another place where a δMOEA
  will necessarily do things much differently.  I think adaptive
  tournament sizing is original to Borg.
* Triggering restarts.  This uses a stagnation measure.  I'm a
  little suspicious about this.  It's the "what if we just ran a
  little longer" problem.  You're never going to get it right,
  because it's impossible to know whether you were just about to
  make a breakthrough.
* Injection proportional to pop sizing.  This originates with
  εNSGAII, and is a very good idea.

In short, I like the things that auto-adapt based on population size,
and I'm suspicious of things that try to auto adapt based on
perceived search progress.

This whole note is promted by the appendix to Deb and Agrawal 1999
(the Niched Penalty paper) where SBX and PM are defined.  The
original idea for PM has the distribution index and probability of
mutation changing over time on a kind of "cooling schedule".  (My
words, not theirs.  There is a good idea in there.

## What Happens When Exhaust a Region?

Suppose we exhaust a region.  By this I mean we have sampled a
region around the current Pareto approximation so thoroughly
that we've run out of points to sample in the neighborhood.
What is our approach to variation operators when they start
producing offspring we've already sampled?  We could decrease
DI and try again?  Or we could take a vector from the parent to
the child and continue stepping along it until we find a point
that's not taken?

So if we take the strategy of using parent-to-child as a suggestion
of where to put the child, then we've got a very interesting thing:

Say we do this:

1. Generate offspring using operators.
2. While already sampled and not at the edge of the space
    Take another step along the vector from parent to
    offspring, in index space, with the biggest component
    equal to delta and the fractional indices accumulated a
    la bresenham.  (Except with floating point math, I'm not
    that masochistic.)  (Alternatively, we could saturate at
    the edge but step all the way to a corner before giving
    up.  This helps if we have binary variables involved.)
4. If we found an unsampled offspring, return it, otherwise 
   generation failed.
5. If generating offspring fails too many times, we've converged
   for all intents and purposes.
   This also goes for random-uniform on the decision space.
   If it keeps failing, that means we've essentially converged.


# Popularchive Layout

Just had an idea about this: whenever we do a sort and
find ourselves altering a tier of the popularchive, we move
onto a fresh and untrammeled part of the popularchive and just
copy over all the rows that need to be copied.

Or we use invalidation flagging.  That works too, with way
less bookkeeping.


# DOE

So I've been fretting about how my DOE is OFAT when a
fractional factorial design is supposed to be much better.
I did some googling and found this abstract:

> FRANKLIN and BAILEY (1977) provided an algorithm for
> construction of fractional factorial designs for estimating
> a user specified set of factorial effects. Their algorithm
> is based on a backtrack procedure. This is computer
> intensive when the number of factors is not small. We
> propose a stochastic search method called SEF (sequential
> elimination of factors) algorithm. The SEF algorithm is
> a simple modification of the exhaustive approach of the
> Franklin-Bailey algorithm since defining contrasts for the
> design of interest are chosen stochastically rather than
> choosing them in a systematic and exhaustive manner. Our
> experience shows the probability of success of obtaining
> a required design to be sufficiently large to make this a
> practical approach. The success probability may be expected
> to be rather small if the required design is close to a
> saturated design. We suggest the use of this stochastic
> alternative particularly when the number of factors is
> large. This can offer substantial savings in computing
> time relative to an exhaustive approach. Moreover, if the
> SEF algorithm fails to produce a design even after several
> attempts, one can always revert back to the Franklin-Bailey
> approach.
> 

Bibtex, if I ever need to look this up:

```
@article{liao1999stochastic,
    title={A Stochastic Algorithm for Selecting of Defining Contrasts in Two-Level Experiments},
    author={Liao, CT and Iyer, HK},
    journal={Biometrical journal},
    volume={41},
    number={6},
    pages={671--678},
    year={1999},
    publisher={Wiley Online Library}
}
```

Backtracking is complicated!  100 DVs, which is my
standard for "a reasonably large number", is basically
going to kill Franklin- Bailey, and I don't have high
hopes for SEF either.  In a hilarious turn of events,
it appears that descendants (SELC) of SEF use GAs to try
to minimize aliasing!

So, in short, don't worry about fractional factorial
designs since it's almost always going to be too
complicated and expensive to find them.

# Objective Space Focus

I think this has to do with EA authors' insistence on
playing by the rules of nonlinear optimization.  Those
rules say that the way we measure the performance of
an optimization algorithm is by its objectives.  This
misses the point due to two levels of uncertainty:
one is that any computational model of a physical system
is going to have some degree of uncertainty involved
in its outputs.  But there's also a higher level of
uncertainty here, which is that we're not sure we've
chosen the right objectives in the first place.

# Hardware Advances

Archiving all, or at least a very large number of,
evaluated individuals is possible only because modern
microcomputers have more main memory by three to four
orders of magnitude than did those available during the
early development of MOEAs in the 1990s.  A basic
assumption held over from that time is that it is
necessary to discard the results of old evaluations
to make room for new.  This assumption no longer holds.

# Philosophical Advantages of Gridding the Decision Space

Gridding the decision space has a pronounced advantage
over gridding the objective space (as in ε-dominance):
the grid spacing is not tied up with value judgements
about the objectives.  Instead, it can be chosen to
reflect the degree of control available over a physical
system.  Many electrical and mechanical components, for
example, have their attributies specified to within a
given tolerance.  Adjusting the values specifying such a
component by less than the tolerance does not produce
a practical difference in the design.
