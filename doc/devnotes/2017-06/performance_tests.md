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

The problem is that the metadata table itself is going to
have some variable fields.  Well, it doesn't have to.

## Problem Metadata

* Problem ID
* nickname (text)
* description (text)
* family (text)
* N Decisions
* N Objectives
* N Constraints
* N Tagalongs
* evaluations table name (text)

We'll set up Problem Metadata by hand whenever we're
making a new problem.

## Decisions

* Problem ID
* number
* name
* lower
* upper
* delta

## Objectives

* Problem ID
* number
* name
* sense
* epsilon

## Constraints

* Problem ID
* number
* name
* sense

## Tagalongs

* Problem ID
* number
* name

## Run Metadata

* runid (uuid)
* Problem ID
* Target NFE
* Algorithm
* Commit ID

## Run Timing

### Starts

* runid
* start time

### Completions

* runid
* end time
* nfe
* reason for termination

### Evaluations (different table for each problem)

Tables are named `evaluations_nickname` unless there's a
nickname collision.  Each row is an evaluation.

* runid
* nfe
* grid indices
* decisions
* objectives
* grid objectives (objectives evaluated at the grid point)
* constraints
* tagalongs

# I Think That's It

Let's start by setting up a database by hand to see how it feels.

```
CREATE TABLE problems (
    problem_id INTEGER PRIMARY KEY,
    nickname TEXT,
    description TEXT,
    family TEXT,
    ndv INTEGER,
    nobj INTEGER,
    ncon INTEGER,
    ntag INTEGER,
    eval_table TEXT)
```

```
INSERT INTO problems VALUES (
    1,
    "dtlz2_rot.100.2.0",
    "dtlz2, rotated, 100 decision variables, 2 objectives, rotation seed 0",
    "dtlz2",
    100,
    2,
    0,
    0,
    "evaluations_dtlz2_rot_100_2_0")
```

```
CREATE TABLE decisions(
    problem_id INTEGER,
    number INTEGER,
    name TEXT,
    lower NUMERIC,
    upper NUMERIC,
    delta NUMERIC)
```

```
CREATE TABLE objectives(
    problem_id INTEGER,
    number INTEGER,
    name TEXT,
    sense TEXT,
    epsilon NUMERIC)
```

```
CREATE TABLE constraints(
    problem_id INTEGER,
    number INTEGER,
    name TEXT,
    sense TEXT)
```

```
CREATE TABLE tagalongs(
    problem_id INTEGER,
    number INTEGER,
    name TEXT)
```

```
CREATE TABLE runs(
    run_id TEXT,
    problem_id INTEGER,
    target_nfe INTEGER,
    algorithm TEXT,
    commit_id TEXT,
    prng_seed INTEGER)
CREATE TABLE starts(
    run_id TEXT,
    starttime TEXT)
CREATE TABLE completions(
    run_id TEXT,
    endtime TEXT,
    nfe INTEGER,
    reason TEXT)
```

To do decisions:

```
def the_deltas():
    yield 0.3
    yield 0.1
    yield 0.07
    yield 1.0
    while True:
        yield 0.1
deltas = the_deltas()
for ii in range(100):
    query = "INSERT INTO decisions VALUES (1, ?, ?, 0.0, 1.0, ?)"
    name = "decision{}".format(ii)
    delta = next(deltas)
    runs.execute(query, (ii, name, delta))
```

And objectives:

```
for ii in range(2):
    query = "INSERT INTO objectives VALUES(1, ?, ?, 'MINIMIZE', 0.1)"
    runs.execute(query, (ii, "objective{}".format(ii)))
```

Let's not forget evaluations.

```
query = "create table evaluations_dtlz2_rot_100_2_0(run_id TEXT, nfe INTEGER, {})"
grid = ["grid{} INTEGER".format(ii) for ii in range(100)]
decisions = ["decision{} NUMERIC".format(ii) for ii in range(100)]
objectives = ["objective{} NUMERIC".format(ii) for ii in range(2)]
grid_objectives = ["grid_objective{} NUMERIC".format(ii) for ii in range(2)]
query = query.format(", ".join(grid+decisions+objectives+grid_objectives))
runs.execute(query)
runs.commit()
```

# Spinning up Runs

With the problem definition out of the way, I'd like to
start spinning up runs.  That means altering my performance
comparing scripts so that they database their results.
(We can put off for now writing the script that sets up
a problem.  I've captured all of the steps and I can work
on that while runs are going.)

This brings us back to the ZMQ question.  The only thing I
really need at this point is a data sink.  Naturally I want
to run that on PC9, since that's where I do everything.

Actually, before I even get to ZMQ, why not just write
a slightly different wrapper than the CSV-writing one,
that connects directly to a sqlite3 file and just does the
equivalent of the CSV writing, but straight to database?
That's going to get me off the ground fastest.

# 30 Runs Later

2017-02-23 20:25

I did 30 seed runs of UDMOEA on 100/2 rotation 0.  To do
30 runs of Borg, I need to set Borg up the same way I
did UDMOEA.

Equally important, I need to set up metrics.  Recall that
I want to see HV and epsilon-HV evolving over time.  Also,
I wanted to come up with a metric that respected decision
space.  What if I do this: take every evaluation ever.
Pareto Rank them all by grid_objectives.  Figure out
their grid indices.  Now we have a rank for each set of
grid indicies.  Now, for every NFE, determine the archive
of each MOEA and determine which grid boxes its archive
occupies.  Then average (median?) the rank of the occupied
grid boxes is your metric.

See analysis in my ongoing ipython notebook, which I've
hooked up to the database.

2017-02-23 21:18

# Borg

2017-02-24 08:51

My strategy for Borg will be to copy the UDMOEA runner
and have it do the same thing, except with Borg.

2017-02-24 10:58

It's running now.  The next thing to do is... actually
I'm not sure.

Maybe I want a tool for defining different problems?

Maybe I want to be able to do parallel runs?

Doing parallel runs means I really want to do the
databasing on PC9 while distributing runs to other machines
(16 and 19 mainly).

My first step in that direction is to write the
single-machine multiprocessing version of this.  It will
spawn as many runs as it can afford the memory for.
(Not too many for UDMOEA, because of its intentionally
hefty memory requirement.)

How much memory am I using?  I'd allow 4G, although I don't
think it's quite that much.  With room for the OS and other
userland stuff, that only lets me do 3 runs in parallel.

Do note that this is not something I consider a general
problem.  The big memory allotment is partly due to my
choice of a problem with 100 variables and partly due
to the 100x10000 archive.  These numbers were chosen on
purpose to take advantage of modern hardware.  The only
people who are going to want to run actual instances of
UDMOEA in parallel are me, i.e. anybody who wants to do
an algorithm shootout.

But at any rate, it means that we would be well served
to mix and match, so that we don't have more than a few
UDMOEAs going at once.  The alternative there is to try
out shelve, at a massive hit to performance.  Or maybe use
a memmapped SQLite database.  Also probably at a massive
hit to performance.  I potentially prefer the latter.

But never mind.  Just because we can address memory use,
doesn't mean we should.

Oooh, and then there's metrics.  So much to do.

Non-metrically speaking, after 30 seeds, Borg appears
to have a slight advantage.  But again, I need metrics
to make it clearer.  Also, I want to have metrics over
time, to make the case that we do better in the early
part of the run.

# Next Step: parallel

2017-02-24 13:02

So the plan is, we work out a simple multiprocessing-based
parallelism and use it to do another dtlz2 100/2 problem
rotation.

How's that going to look?

The evaluation function is going to look a lot like the
one in the current databasing_results template, except
it's not allowed to do its own sql queries.  Far and
away the simplest thing to do from my point of view
is to turn every `connection.execute` into a multiprocessing
queue push.  Although if I'm going to go that far, why
not just go all the way and use ZMQ to truly separate
processes?  If we assume the processes don't crash, the
main process can just spin up the optimization runs
and the optimization runs can connect to a PULL socket
that vacuums up the results.

Setting up a problem:

```
sqlite3 runs.sqlite3 "INSERT INTO problems VALUES(2, 'dtlz2_rot_100_2_1', 'dtlz2, rotated, 100 decision variables, 2 objectives, rotation seed 1', 'dtlz2', 100, 2, 0, 0, 'evaluations_dtlz2_rot_100_2_1')"
```

And in ipython:

```
runs = sqlite3.connect("runs.sqlite3")
ndv = 100
nobj = 2
rotation = 1
nickname = "dtlz2_rot_{}_{}_{}".format(ndv, nobj, rotation)
tablename = "evaluations_{}".format(nickname)
query = "create table {}(run_id TEXT, nfe INTEGER, {})"
grid = ["grid{} INTEGER".format(ii) for ii in range(ndv)]
ndv = ["decision{} NUMERIC".format(ii) for ii in range(ndv)]
objectives = ["objective{} NUMERIC".format(ii) for ii in range(nobj)]
grid_objectives = ["grid_objective{} NUMERIC".format(ii) for ii in range(nobj)]
query = query.format(tablename, ", ".join(grid+decisions+objectives+grid_objectives))
runs.execute(query)
runs.commit()
```

# Parallel Problems

Parallel evaluation seems to have a distinct problem.
Using msgpack and sqlite3 adds so much overhead that it
would be faster to run in serial!  Lose, lose.  This is
the problem with databasing so much stuff!

In principle, if my runs are completely repeatable, I
can reproduce any given run without keeping all of its
evaluations.  As long as my metrics *don't* include the
heavy-duty rank-occupancy metric and I can reference my
Pareto fronts to 0, I can at least do HV and epsilon-HV
in parallel.  Then the only stuff I have to database is
metadata and metrics.  Metrics are so much lighter that
they're cheap to send and receive, unlike full evaluations.
And you can roll big runs up into a single array....

Actually, why send a single message when most of the time
we want executemany?  We might be able to cut the overhead
and keep the structure.

Nope, doesn't seem to have helped.  No, the way to go
here is to figure out the metrics in advance, make
UDMOEA use mt19937ar for total repeatability, and
compute the metrics during the run.  Forget about
keeping the evaluations -- it's great for pretty pictures,
but not sustainable from a data perspective.  And
in the end it would be faster to repeat the runs
and recompute the metrics than it would be to keep all
of the evaluations.  It might even make sense to wait
until the very end of the run to send the metrics over.

2017-02-24 16:52

So what does this mean for this weekend?  I'm not starting
up any runs for over the weekend.
