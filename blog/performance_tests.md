# Performance Tests

2017-02-21 14:35

For all of these tests, deltas follow this pattern: 1.0, 0.3, 0.1, 0.07, 0.1, 0.1, 0.1,.....
We do 5000 nfe max, although UDMOEA is allowed to stop early.

## DTLZ2 4,2

Stipulating that we are only interested in
seeing a single sample per grid point, UDMOEA smokes Borg
in this test, but only because it recognizes that the grid
is sampled out and stops running, while Borg tries forever
to keep going.  So score 2 for grid search, 1 for UDMOEA,
and 0 for Borg.

Grid search 2, UDMOEA 1, Borg 0

## DTLZ2 100,2

This is somewhat more equivocal.  The at-grid-point
objective values for UDMOEA still handily dominate those
for Borg, because the Pareto approximation is (1,0)
and (0,1), but if we look at the actual objective values
realized by Borg, Borg has a much better spread.  Granted,
this is because we defined the deltas in such a manner
that UDMOEA would never be able to find the middle of the
Pareto front in the non-rotated versions.  With 100 DVs,
grid search is completely toast.

Grid search 0, UDMOEA 1, Borg 1

## DTLZ2 rotated 100,2

This experiment shows where UDMOEA is weak.  Neither MOEA
gets anywhere near the Pareto set, and maybe things would
be different if we allowed a longer run.  But despite
wasting about 4% of its evaluations, Borg still comes
out ahead.  Also, UDMOEA is really sensitive to its DOE
here, and will fail if it doesn't hit enough corner
points.

Grid search 0, UDMOEA 0, Borg 1

## Final Score: Grid search 2, UDMOEA 2, Borg 2

So it's a tie, in this quite unscientific (three problems, one seed) experiment.

# Theories

2017-02-21 16:54

## Sparsity of Effects Doesn't Work Out How You Expect

Maybe it's not as simple as I thought, and changing more variables at once is ok?  I could go either way on this argument.

## Selection Favors Rank 0 Too Heavily

This is a really clear flaw in my implementation.  The heavy weighting on rank 0 discourages diversity.

## Or Maybe I Should Just Parameterize SBX Differently

I'm not sampling the interior.  Maybe I just need to change
how I parameterize SBX so that I do.

## It's the Epsilons, Stupid!

Perhaps the most blindingly obvious point is that, for
large spaces, just because you have a delta grid doesn't
mean you don't need an epsilon grid.  I think the 100 DV
instance might be suffering from that, although possibly
not.  Here are the numbers on rank occupancy after 5000
nfe

rank    size
-----   -----
0       167
1       178
2       196
3       179
4       189
5       174
6       157
7       158
8       142
9       148
10      133
11      138
12      143
13      141
14      137
15      129
16      126
17      128
18      121
19      115
20      121
21      117
22      96
23      97
24      96
25      85
26      79
27      80
28      86
29      87
30      89

167 isn't insane for the archive.  Let's see how the
50,000 nfe run goes.  Might as well see where Borg goes
after 50k too.  In the morning.

## I smell a rat

Wait, what's this?

```
tail -n1 udmoea_dtlz2_rot_100_random.csv
0,0,21746,1,2,5,7,1,0,5,5,0,5,5,5,5,5,5,5,0,5,5,0,5,0,5,5,5,5,5,0,5,5,5,5,5,5,0,5,5,5,0,1,5,5,5,5,5,5,5,0,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,1.0000,0.6500,0.5000,0.5000,0.1000,0.0000,0.5000,0.5000,0.0000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.0000,0.5000,0.5000,0.0000,0.5000,0.0000,0.5000,0.5000,0.5000,0.5000,0.5000,0.0000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.0000,0.5000,0.5000,0.5000,0.0000,0.1000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.0000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,0.5000,5.4543,6.9982,5.4543,6.9982
```

Notice all of those fives?  Especially the unbroken string of fives at the end?  And this from the purportedly random DOE sample?


Consider these lines of code from Sampling.py 

```
elif stage in (RANDOM, EXHAUSTED):
    grid_point = grid.GridPoint(
        *(state.randint(0, len(a) - 1) for a in grid.axes))
    # transition out of RANDOM is if we have too many failures
    doestate = doestate._replace(counter=doestate.counter + 1)
```

Do they do what you think they do?

Why all the fives?

Forehead-slap: we were doing OFAT instead of random.

# It's Not the Epsilons or Selection

2017-02-22 12:24

The top biggest win is random sampling instead of OFAT.
CORNERS is almost certainly a waste of time and I should
get rid of it.
The next biggest win so far was relaxing the sparsity of
effects assumption to peak around 3 decisions.
The current linear selection ramp seems to be working
better than any alternatives.

Granted, we're looking at 60k evals on one seed, so this
is hardly a Sobol' study.

However, the win from peaking at 3 decisions is decisive
enough to sway me.

# What's Left?

So much.  Let's consider why Borg might still be winning.

1. It still might be epsilons.  Supporting evidence is that
after 60k nfe, Borg's archive dominates UDMOEA's, and has 17
members.  UDMOEA's Rank 0 has 465 members.  Ouch.
2. Restarts provide more diversity.  If you look at where
Borg samples, in objective space, it's all over the place.
3. Adaptive multi-operator search.  Seems unlikely for
all kinds of reasons.

# It's Epsilons After All

Specifically, selection does nothing to favor diversity in
objective space.
465 archive members is a lot.  We know from microGA that
a small population evolves fast.

So what do you do?  Pick a target selection size.
If your rank size is greater than the target selection
size, come up with an objective-space gridding.

Suppose we were to normalize the objective range in
the rank to 1.0, for each objective.

Then if you grid at 0.1, you have on the order of 10**nobj
solutions, depending on the shape of the tradeoff.

So if you set target selection size to 20, then you
choose a grid as follows.

```
g**nobj<= 20
g <= 20 ** (1/nobj)
```

Where g is the number of steps.

Now, this will work with a modest number of objectives.
2 objectives gives you a 4x4 grid.  That's a little at odds
with observation.  Maybe it's (gridding)**(nobj-1).

```
g**(nobj-1) <= 20
g <= 20 ** (1/(nobj-1))
```

That gives us a 20x20 grid.  Which would be OK for the DTLZ2 example.

nobj    gridding    estimate
-----   ---------   ---------
2       20          20
3       4           16
4       3           27
5       2           16
6       2           32

But above 6 objectives, the space starts to expand
explosively, and you can't go below a gridding of 2.
The only thing that helps you here is the same thing that
helps Borg.  Real problems have correlated objectives,
so the gridding doesn't work out how you'd think.

2017-02-22 13:57

So is gridding a good idea?  Well, it's working for Borg.

Anyhow, suppose we've gridded out the rank from which
we're selecting.  Then determine what objective box Parent A
is in and randomly draw Parent B until we hit an individual
in a different objective box.

You know, we could do something even simpler.  We could choose
the objective with the flattest distribution and divide it into
20-30 steps.  Then insist that Parent B not be in the same step.

How do we measure flatness?  Standard deviation over range
would be adequate.

[Wikipedia](https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance#Online_algorithm)
has the "online" version of the variance computation.

2017-02-22 16:21

So I implemented that procedure.  The simple one using flatness.
It did not go beautifully.  With a grid of 30, it was comparable
to my first run that tuned sparsity of effects to peak at 3.
I tried 10 and 40 also, both were inferior.  10 markedly so.
I'm trying 20 now.

I do believe there's a sweet spot there.

I could also try doing epsilon Pareto sorting or its moral
equivalent, but I'm reluctant to do so.

Maybe we could do adaptive epsilon Pareto sorting on rank 0 to
pare down the pool of alternatives for parent_a.

Result of 20: about the same as 30.  Binary search suggests 25, but
I don't see this as a winning game.  I'll try it anyhow.

# Back to Epsilon Sorting

2017-02-22 16:34

Let's reflect again on the benefits that Borg gains by
having an epsilon dominance archive.  Selection will
always favor the bottom-left corner of the epsilon box,
and this pushes the front forwards.  We can most definitely
take the same approach by using epsilon dominance for
selection.

(Interlude: run result.  grid=25 is markedly inferior.
2017-02-22 16:40.  Conclusion: worse than I thought,
this gridding approach is sensitive and unstable.)

Adaptive versus nonadaptive:

The nonadaptive (borg) approach will tend to favor whatever
weighting the epsilons describe a priori.  The adaptive
approach will tend to favor whichever objective has the
smallest range in rank 0.  This is dangerous because it
will reinforce the winners.

Conclusion: we have a problem.  Adaptive epsilons are
appealing because they mean we don't have to parameterize
them.  But they will have a runaway effect.

2017-02-22 16:51

One more thing before I give up on flatness.  What if I
used the minimum-flatness objective?  Indifferent result.
Same as max-flatness.  Maybe because DTLZ2 is so
symmetrical.

## Adaptive / Nonadaptive

How do we fix this?  As we improve an objective, its range
decreases and we reward it more by exaggerating it for
in-box selection.

2017-02-22 20:24

Further thoughts.  So what if in-box selection gets
exaggerated?  Unlike nonadaptive epsilons, we don't end up
with certain points getting all the attention.  Instead we
adapt as the front moves.

Well then, what would be the point of focusing on certain
points at all?

Maybe the issue isn't epsilons after all.  Maybe it's the
lack of diversity.  Suppose we did "continuous injection",
by which I mean 10% of the time we just do uniform mutation
on Parent A instead of SBX.

Let's try that next.  I can't see how adaptive thinning
would help.  The thing about nonadaptive epsilons is that
they really do prioritize certain points in the space.
That means there's a whole lot of pressure to improve
a small number of points, even as the front moves.
All we can hope to do without going all the way over to
nonadaptive, fully parameterized epsilons, is to keep the
search moving forward a little bit on a broad front.

Let's pause to recognize that this is a real achievement of
epsilon-dominance archiving.  When there are a lot of DVs,
the objective-space difference between a grid search and a
search on a continuous space declines.  Epsilons make it
possible to deal with dominance resistance, which we're
seeing even with two objectives.

So I'm going back on what I said.  Without some kind of way
to thin the selection, we're stuck making marginal
improvements.  But what exactly is the advantage?  What
really?  Suppose we have my rank 0 and Borg's epsilon
dominance archive.  Suppose they're at the same place.  A
reasonable assumption considering I start out ahead and then
Borg catches up.  So in this case, my rank 0 is a superset
of Borg's archive.  Borg also has a populaiton mainly
consisting of mutated archive members.  I have a population
consisting of my archive.  Borg does tournament selection.
That means it can easily end up choosing one parent that's
not in the archive.  But we do ramped rank selection for 
parent b, which isn't far from the same thing.

Because of decision-space gridding, my rank 0 is guaranteed
to be adequately diverse.  As are all my ranks.  So sampling
from my archive should be fine.  I should not be at a
disadvantage to Borg.  Then the problem must be a lack of
diversity?

This takes us back to the experiment.  Let's do it.
Continuous injection.

2017-02-23 07:55

Holy cow, was that a success.  We're in the mix with Borg
after 60k, converging to around radius 2, just like Borg does.
Borg is only slightly dominant.  We could maybe improve
a tiny bit further by tuning continuous injection.  10% is
almost certainly too aggressive.  That's like Borg doing a
restart every 900 NFE for a population of 100.  Well, actually,
that's not too far off, especially when Borg detects stagnation.

Performance tuning time is done for now.  Let's have us a
shootout!

Well, first...

1. Cherry-pick the relevant commits back to the main repository
from the performance comparison repo, to keep the main repo
clean and up to date.
2. Whip up a job runner and a databasing scheme.  Flat files
are killing me.
3. For goodness sake, preserve the NFE with the evaluation
(at return time) so that we can have NFE and final rank at the
same time.

But even before that, because I like to feel good about myself,
let's animate the Borg versus UDMOEA evolution history.

2017-02-23 12:01

That took a while, but was worth it.  A much better picture of
how evolution works.  And we're smoking Borg, especially early
in the run.  This is even considering that we set the delta on
variable 0 to 1.0, meaning there's a huge space where Borg is
allowed to optimize, where we aren't.

So, revisiting the to-do list:

1. Get the main repo up to date.
2. Build the testing infrastructure.

2017-02-23 12:22

Did 1, but I realize my initial DOE is hard to use right, so
let's fix that before proceeding.

2017-02-23 12:53

Fixed.

# Configurable, Repeatable, Parallel Tests

In this case I don't see a strong need to have a ZMQ-based
job distribution system.  I'll just write a multiprocessing
wrapper... wait, I want everything in the same database.
OK then, we're going to do this a little differently.

The only thing I really need here is a process that sits in
front of SQLite and crams results into it.

So my resultifier gets messages...

```
runid
topic
details
```

Where details depends on topic.

```
runid
topic: "run description"
details:
    family: dtlz2 rotated
    decisions: 100
    objectives: 2
    rotation seed: 0
    MOEA seed: 0
```

Each family gets its own table for extra keys, like rotation seed.


Maybe I should start with my table format.

Evaluations:

* runid (uuid)
* nfe
* grid indices
* decisions
* ...

OK, problem here.  Seems like every problem has its own
table layout and formatting.  Indeed, a lot like the CSVs
I was dumping out.

Well, that's OK, we just have a different table for each
problem.  Then we also make a metadata table that explains
what each problem is.
