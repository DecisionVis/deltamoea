# Computing Metrics

2017-02-26 20:14

Hypervolume.  That means I should pull down my hyppy repo.
If I recall correctly, I was working on a pretty solid
Python wrapper for it when I ran out of time to work on it.

2017-02-26 21:09

So I dusted off the hyppy repo.  It appears to be pretty
sound.  I'm going to want to check the results before use.
Fortunately the WFG website has copious test sets.  I hope
they still have them...

2017-02-26 21:23

Ah yes, yes they do.  And they've revised the wfg
algorithm.  Twice.

I'd rather that than have the resources disappear from the
internet, but this does throw a bit of a wrench in the
works.  My shiny frontend to WFG isn't going to work with
the changes they've made.  And I imagine they didn't focus
on fixing memory leaks and enabling continuous runs like
I did.

Probably the best option here is to take their new code,
run it against some sample data sets, and check that the
outcome is the same as with my old code.  Then use the old
code.

Or, I take their new code, leaky or not, on the assumption
that it's likely either faster or more correct, and
probably both.

Going back to the first hand, no, I want to use
metricsystem.py.  I shudder at how much less userfriendly
the C version is.  In the long run, it would be a service
to everybody involved if I got the Python code running with
an up-to-date verison of the C code.  It even takes "-" as
a filename argument!  Of course I could import it and not
even use the cli.

2017-02-27 10:39

How I'm actually going to use it: since it uses WFG (my
forked libwfg2.so) for the calculations, there's a good
possibility that I could do this in a multithreaded
fashion without falling victim to the GIL.  That avoids
the communication overhead of the multiprocessing approach.
Then at the end of the run, we have the main thread send
a single batch of metrics over to the databasing process,
whichever machine that's running on.

As far as calling wfg, on closer inspection metricsystem
is a whole bunch of command-line convenience stuff.  I
want wfg.py by itself.  Just send it a list of lists,
appropriately transformed (it assumes minimization,
so I need to send it negated objectives even though
I'm also doing minimization, because I want to zero-
reference the hypervolume computation).

2017-02-27 11:32

To do:

1. Produce an updated udmoea problem runner that uses
mt19937ar.py, so that we have repeatable runs.
2. Write the multithreaded hypervolume computation so
that we can compute metrics concurrently and verify that
we're at 200% CPU.
3. Develop the databasing schema for runs / metrics.
Ideally I want to be able to define runs in the database
in such a manner that I can reproduce them completely from
the database.  And I do mean completely --- the ultimate
would be sending the whole working tree over the wire,
and having the worker unpack and run it.  Actually that's
insane.  Let's settle for sending a commit ID and having
the worker check it out.
4. Actually spin up some runs.

# Step 1: Repeatable Runs

Big problem with rotated dtlz2: we're using the 
interpreter's RNG, which doesn't fill me with confidence
when it comes to repeatability.

We'll solve that second though.  The first thing to do is
ensure that UDMOEA actually works with the Python Twister.

OK, so it ran without crashing, that's a start.

Animation shows that it's comparable in performance to the
UDMOEA that uses the native PRNG, so that's a second source
of confidence.  I can't do metrics comparisons, since
that's the whole problem we're trying to address in the
first place.  On the plus side, my design for inserting
a different RNG was ridiculously easy to use.

So back to the second problem -- the random matrix.

## Random Rotations

The solution to the random rotations problem is that this
database is going to become DTLZ2 specific.  That eases
a lot of pressure on my schemas, along with only keeping
metrics.  In this database, I will store the rotation
matrix.  All participants in the study will then construct
their rotated DTLZ2 instances from the matrix in the
database.

```
CREATE TABLE rotation_matrix (
    problem_id INTEGER,
    rownumber INTEGER,
    colnumber INTEGER,
    value NUMERIC
)
```

Now, we also need a `dtlz2_problem` table.  It will look
like this:

```
CREATE TABLE dtlz2_problem (
    problem_id INTEGER PRIMARY KEY,
    decisions INTEGER,
    objectives INTEGER,
    comment TEXT
```    

This schema allows rotated and non-rotated versions to
coexist peacefully.  Non-rotated instances just use identity
as their rotation matrices.  We'll use the comment as a
description.

Now, a problem by itself does not suffice to do a run.
We also need to reference the MOEA code itself.  That's
why we need a `dtlz2_runs` table.

```
CREATE TABLE dtlz2_runs (
    run_id INTEGER PRIMARY KEY,
    problem_id INTEGER,
    commit_id TEXT,
    algorithm TEXT,
    max_nfe INTEGER,
    prng_seed INTEGER)
```

With this information, we have enough to perform the same
run a second time and hopefully obtain the same results.

Indeed, the workflow I have in mind is to do all runs this
way:

1. Create problem
2. Create runs
3. Start job queue
4. Start database writer
5. Start workers
6. Start job submitter

The job submitter will find runs that have no starts and
start them.  Optionally it will find runs that have no
starts for a specific commit id.  Optionally it will
resubmit runs that have no completions instead.  Optionally
it will resubmit runs unconditionally.

All this implies we have the `starts` and `completions`
tables defined much as before.

```
CREATE TABLE dtlz2_starts (
    start_id INTEGER PRIMARY KEY,
    run_id INTEGER,
    starttime TEXT)
```

```
CREATE TABLE dtlz2_completions (
    start_id INTEGER,
    endtime TEXT,
    nfe INTEGER,
    reason TEXT)
```

Note that we have a hierarchy here: problem -> run
-> start.  A start is at the lowest level.  Two starts
of the same run _should_ produce identical results.  But
things fail or get cancelled.  Starts get created because
that's the first thing the metrics thread does when it
spins up.  Since it communicates with the DB writer, it
tells the DB writer that it's starting a run.  The DB
writer responds with the `start_id` and the metrics thread
can use that subsequently.

In addition, the whole point of this exercise is to collect
metrics.  As discussed, the worker will compute metrics
periodically in a separate thread.  The computing thread
will then send them to the database writer (this is the
one place where we're going to use ZMQ).  Sending isn't
going to happen often, probably just at EOR or every
100,000 evaluations, whichever comes first.  I don't plan
on running out to 100k very often, I'd rather do more
problems and more parameterizations.

At any rate, database writer gets metrics and writes them
out to the database.  Therefore I need a table that looks
like this:

```
CREATE TABLE metrics (
    start_id INTEGER,
    metric TEXT,
    nfe INTEGER,
    value NUMERIC)
```

This is a much simpler schema than I was pursuing initially
and it requires much less data.

# To Do List

2017-02-27 13:49

This is somewhat revised then:

0. Start jobrunners
    Jobrunners are what spin up actual workers.  They take
    care of cloning the repo to a temporary directory and
    spinning up a worker there.  They ask for jobs using
    a REQ socket and disconnect / reconnect the socket if
    they get a SUB message that tells them to.
    Jobrunners can use git, so they need to have a 
    deployment key at least on each machine.
    Because the jobrunners run on the worker machines, 
    they are the ones I want to have to restart the fewest
    times.  Ideally I'd like them to be able to do a git
    checkout and restart themselves, so that I never have
    to ssh over to the workers.
    Workers themselves connect to a req socket to talk to
    the DB writer, and that's it.
    Arguments: job socket, status socket, temp directory,
    number of workers to spin up.
1. Start job queue
    Spin up a job queue.  Starting to think it should bind
    REP sockets to talk to the jobrunners, with in addition
    a PUB socket that tells the jobrunners to reinitialize.
    (We use the PUB socket if we need to restart the queue
    but don't want to restart the workers.)
    Also needs to bind a REP socket that tells the job
    submitter that a job has been accepted.
    Arguments: the three sockets.
2. Start database writer
    Arguments: database filename, REP port to bind.
3. Create problem
    A script that writes a problem into the database.
    Arguments: database filename, ndv, nobj, optional
    prng seed.  No seed means identity matrix for rotation.
4. Create runs
    A script that creates runs in the runs table.
    Arguments: database filename, problem id, algorithm,
    start seed, end seed, max nfe
5. Start job submitter
    Arguments: database filename (from which to get a list
    of runs to submit.)  REQ port to bind for talking to
    the job queue.  REQ port workers need to use to talk to
    the database writer.

So, what does the job submitter ask for, exactly?

* commit to check out
* script to run
* arguments to script
    - n decisions
    - n objectives
    - socket to connect for the DB writer
    - rotation matrix (we need to provide this somehow...
      stdin? long argument?)

I see steps 3-5 being wrapped up in a convenience script.

How do we know what the status is?  The DB writer has a
rough idea, should we use it?  Bind another REQ socket for
status requests?  The DB writer knows what problems have
been defined, what runs have been defined, and what jobs
are in flight and how long they've been running.

So maybe my conveniece script is a whole curses UI that
lets me manage my cluster.  If I get that far.  That's a
thing to do while waiting for results if I'm not otherwise
engaged.  Probably not a thing to spend a lot of polish
on.

Simple experiment: The subprocess library lets you Popen
a process that survives you.  Excellent.

# What Next?

2017-02-27 16:20

I sketched out CLIs for all of the scripts involved.
Now to start implementation.  I'll start with the UDMOEA
worker.  It couples with the database writer, so I'll
start there by writing a stub that just binds the socket
and echoes.

2017-02-27 16:33

Writing the echoer was easy.

2017-02-28 09:06

One other thing -- deltas and epsilons.  I'm going
to hard-code them for now, just like all of the other
parameterization is hard-coded.  It's just one more
thing, and I can't be bothered at this point.

2017-02-28 10:54

Why are my hypervolume numbers wrong?  Am I wrong about
assuming minimization?  Yup.  `metricsystem` assumes
minimization.  `wfg.py` assumes maximization.

2017-02-28 12:08

Actually, I need to be computing HV relative to a nadir,
probably 10, 10, ...
The reason is that weird axis fliers capture a lot of
hypervolume relative to the origin.  Relative to a nadir,
they add negligible hypervolume, and they make it so that
hypervolume is a strictly increasing function of nfe.

For Borg, we want to collect both HV and grid-HV, and in
both cases what we actually compute will be epsilon-HV.

# Failure Patterns

2017-03-01 08:38

Working through how things fail, the worst case is if the
DB writer fails, the jobrunner will need to be restarted.
But that's what its SUB socket is for.  The workers should
check out after blocking for a minute unable to talk to
the DB writer, so the whole process is pretty hands off.
Ideally, I don't have to stay logged into the worker
machines.  Start a jobrunner with nohup and appropriate
socket arguments, and we're off to the races.

# Things That, For Now, Are Hard-Coded

2017-03-01 10:47

It might make sense for some or all of these to be captured
in the database:

* epsilons
* deltas
* nadir point

For now, the fact that I keep everything under version
control means that the commit id should be adequate to
capture the conditions of the run.  So putting these
things in the database isn't necessary, but it would
certainly be more transparent.

# Unanticipated Weirdness: In Which A Complex System Exhibits Emergent Behavior

2017-03-01 13:15

It's not that complex a system, either, but when I run
the current UDMOEA worker with the database writer, the
database writer eventually gets behind.  This applies
backpressure to the workers, all at the same time.  They
all pause optimization, and PC16 goes idle while the db
writer catches up.  They have sufficiently long pauses
that none of them dies, but at any rate they all come alive
again at the same time.

Solution: db writer should not do a commit every time it
receives metrics.  Maybe every start / completion.

2017-03-01 16:39

The biggest problem I face now is that it's difficult and
potentially errorprone to create new problems and runs,
and then to launch the runs.

`define_problem.py` and `create_runs.py` will handle the
creation side.  But to handle the actual launch, I need
to write a whole bunch of stuff:

* job submitter
* job queue
* job runner


