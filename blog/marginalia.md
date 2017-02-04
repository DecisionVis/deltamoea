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
