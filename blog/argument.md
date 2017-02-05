# Argument

2017-02-04

This is going to be a new kind of MOEA.  Therefore it's quite probable that
we shouldn't use the existing operators.  They assume a continuous decision
space, and we don't exactly.

## Sketch

What does it look like to use MOEADV?

```
import moeadv

x = moeadv.Decision('x', 0.0, 10.0, 0.1)
y = moeadv.Decision('y', 0.0, 30.0, 6.0)

w = moeadv.Objective('w', moeadv.MINIMIZE)
z = moeadv.Objective('z', moeadv.MINIMIZE)

moea = moeadv.Moea(decisions, objectives, constraints)
```

## But Wait

How soon we forget.  I already have a running moeadv.

But it's at a very basic state of development right now.

And it had a bug.  What was the bug?  And what are the
shortcomings?

And furthermore I need to write one of these in C, ideally
in a way that precludes the need to do dynamic memory allocation.
Or at least the need to do frequent dynamic memory allocation.

Let's start with the basic data structure.  Suppose we have
gadjillion decision variables and each one has a resolution 
of ten steps.  And by a gadjillion, I mean 100 decisions.  So
10 to the hundredth power is obviously way too many to store
in memory.

This means we discard the simplest structure, which allocates
enough space for every possible solution.

The next structure is a flat list of rows.  This structure is
good enough.  It's certainly not a fancy CS data structure, but
it has the advantage of being allocated once.  It's searchable
in O(n) time, and we can provide a strong guarantee about its
size in advance.  Basically, the user gets to determine how
much space to use, and that caps the population size.  Once we
use up the space, we discard the least favorable solutions.

So, what are the data structures involved here?

1. A big array of Individuals, the Search Record (or something like
that.  Archive is taken.)  The Search Record helps prevent us from
needlessly reevaluating Individuals by keeping as many previous
evaluations as we can afford.
2. A medium sized array of Individuals, the Population.  This is the
current search population.  It's pretty close to the current Pareto
approximation most of the time, so we don't waste time evaluating
Individuals with a poor chance of success.
3. Another medium sized array of Individuals, the Archive.  This is
the actual current Pareto approximation.

Bear in mind that we're trying to design an MOEA for users whose
function evalution times can be as long as 2 days!  They can
do these in parallel, but it's still slow.  This means we can
afford to take our time and do stuff like sort the Individuals
array periodically, which makes lookup take O(log(n)) rather than
O(n).  Although if it takes 48h to do an evaluation, n isn't going
to be a big number ever.

What does an Individual look like?  An individual is decisions,
objectives, and constraints.  Decisions are integer indices on
the grid.  Objectives are floats.  Constraints are also floats.

4. Another dynamic allocation: arrays of grid points.  This is
our first opportunity to bail OOM, if the user specifies some
absurd resolution.

5. Another dynamic allocation: The array of comparison functions.

Here's why we can't do O(1) indexing with the preallocated array:
Unless we have a "valid" bit for each individual, we can't say 
whether it's been sampled yet.  But that's not something we want
to do for the big array because that just makes it bigger.

I think the limit on sampling / allocation is how long it takes to
search, not how much space we can allocate.
Meditate upon this.

It might be easiest if we kept the arrays sorted by index whilst
also separating by rank.  We can assume that in the ordinary case
we're going to be looking up individuals in the first few ranks,
because we stick pretty close to the current Pareto approximation
during search.  So the idea would be we make, say, twenty ranks.
Each has a huge allocation, say a million.  Is that realistic?
Say we have 100 variables, each taking 8 bytes.  That gets us
closer to 1k per individual.  On the other hand, decisions are
indices, so we don't need that level of precision and can probably
get away with 1 byte per decision in general.  At any rate, we
have between 100 and 1000 bytes per individual in the worst case,
where we have on the order of 100 variables.  So a million is
between 100 megabytes and a gigabyte.  Now we start to look a
bit askance at that huge allocation.  Also, if we want to avoid
the overhead of sorting these chunks, we need to keep them
smaller.  So, suppose we keep 20 ranks of 10k individuals.  Each
rank is then 10k * 1k = 10M of storage, max.  20 ranks then tops
out at 200M.  We could even do 100 ranks then.  That takes us up
to 1G on the outside, which for our purposes is still a pretty
comfortable allocation.

This means that there's no differentiation between population, archive,
and general storage.  The first rank is equivalent to the archive.
If a rank overflows, we just bump solutions into the next rank.  So
what if the ranking gets a little askew when we have more than 10k in
a rank!  We emit a warning in that case anyway, since that's an absurd
number of solutions to have in a Pareto rank, and it means that you've
failed somewhere in defining your objectives, or you asked for too
much precision in decision space.

Another nice thing about this scheme is that we know Linux doesn't
actually allocate a page until you try to use it.  It overcommits, in
other words.  Now, in Python this doesn't help us at all, because Python
has to do bookkeeping on all of these Individuals.  But in C this helps
a lot because we're unlikely to use most of the memory we've asked for.

## Pareto Sorting

Since we're keeping track of several ranks, we have a pretty good story
to tell about sorting: when we receive an evaluated individual, we try
to sort it into the first rank.  If that fails, we try the second rank,
and so on.  The worst case is that you have to scan all ranks completely
before finding out where an individual settles, but the probability
of that is very low.  In general, you're pretty likely to find that
a solution is in a lower rank early on, if it is in a lower rank.
The only time you're likely to scan a whole rank is when the solution
is nondominated WRT that rank.  So in general, we expect about ranksize
comparisons, worst case.  And that's in the unlikely case that our ranks
are full.

The very last rank, until it fills up, can be a dumping ground for 
individuals dominated by all the other ranks.  After that we can have a
policy of purging the oldest.

## Searching 

Things are a little less rosy for searching.  In the worst case,
you have to scan every rank completely before you determine that an
individual has not already been tried.  We mitigate this dismal O(N)
picture somewhat: when few individuals have been evaluated, N is small,
so although we have to search over all N to determine that an individual
has not already been evaluated, which is the expected case.  When many
individuals have been evaluated, the expected case is that an individual
has already been evaluated, and we're most likely to find offspring that
have already been evaluated when searching through the first few ranks,
because in general offspring are close to parents.

The other downside, however, and this is just part of the overhead
we must pay for this algorithm, is that the expected case when many
indidviduals have been evaluated must be paid over and over until we
generate an individual that has not yet been evaluated.  Our only 
mitigation for this might be to limit the number of Pareto ranks retained.

Well, the other mitigation is that we're talking about very expensive
function evaluations in general.  Otherwise it's not worth all the effort
of maintaining all that history to make sure we don't re-evaluate 
individuals.  In fact, this plays directly to the number of ranks the
user wants to maintain.  If function evaluations are expensive, then the
user can decide it's worth the overhead to keep 100 ranks, or more even.

If function evaluations are cheap, then the user can decide it's worth
the occasional miss not to have to search through all those ranks.  And
that's the crucial performance-tuning parameter for my algorithm!

## Additional State

One other thing that may require some preallocation is the DOE state.
