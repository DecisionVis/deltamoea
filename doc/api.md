# δMOEA API

(C) 2017 [DecisionVis LLC](http://www.decisionvis.com)

## The State Object: `deltamoea.MOEAState`

δMOEA works on what is, for Python, a rather unusual
premise.  δMOEA does not employ an object-oriented design.
Instead, δMOEA provides a small set of functions that
produce, consume, and examine `MOEAState` objects.
The `MOEAState` object is a `namedtuple`, making it
immutable.  Any state change produces a new `MOEAState`,
rendering the old state invalid.

## Initialization

Creating a `MOEAState` requires first defining a `Problem`.
The `Problem` is in turn defined in terms of decisions,
objectives, constraints, and tagalongs.

### Preparing a Problem: `deltamoea.Decision`

This is the definition of the `Decision` type:

```
Decision = namedtuple("Decision", ("name", "lower", "upper", "delta"))
```

To define a `Decision`, initialize its fields.  For example:

```
from deltamoea import Decision
decision1 = Decision("decision1", 0.0, 1.0, 0.1)
decision2 = Decision("decision2", 0, 50, 16)
```

`delta` is the grid spacing for that decision.  `decision1`
in this example will be sampled on 11 grid points: 0.0,
0.1, ... 1.0.  `decision2` will be sampled on 4 grid points:
1, 17, 33, and 49.  (δMOEA will split the difference if
the spacing does not evenly divide the range.)

### Preparing a Problem: `deltamoea.Objective`

This is the definition of the `Objective` type:

```
Objective = namedtuple("Objective", ("name", "sense"))
```

To define an `Objective`, initialize its fields.  For example:

```
from deltamoea import Objective
objective1 = Objective("objective1", deltamoea.MINIMIZE)
objective2 = Objective("objective2", deltamoea.MAXIMIZE)
```

Valid values for `sense` are `deltamoea.MINIMIZE` and
`deltamoea.MAXIMIZE`.

### Preparing a Problem: `deltamoea.Constraint`

This is the definition of the `Constraint` type:

```
Constraint = namedtuple("Constraint", ("name", "sense"))
```

To define a `Constraint`, initialize its fields.  For example:

```
from deltamoea import Constraint
constraint1 = Constraint("constraint1", deltamoea.MINIMIZE)
constraint2 = Constraint("constraint2", deltamoea.MAXIMIZE)
```

Constraints, if defined, preempt objectives.  Minimization
constraints are considered satisfied when less than
or equal to zero, while maximization constraints
must be greater than or equal to zero.  δMOEA only
considers objectives when comparing two individuals
if both individuals satisfy all of their constraints.
Otherwise δMOEA compares their constraints.

### Preparing a Problem: `deltamoea.Tagalong`

This is the definition of the `Tagalong` type:

```
Tagalong = namedtuple("Tagalong", ("name",))
```

A tagalong makes it possible to store a value for later
use.  It has no role in optimization other than to
increase how much RAM δMOEA uses.

### Preparing a Problem: `deltamoea.Problem`

This is the definition of the `Problem` type: 

```
Problem = namedtuple("Problem", (
    "decisions",    # tuple of decisions
    "objectives",   # tuple of objectives
    "constraints",  # tuple of constraints
    "tagalongs",    # tuple of tagalongs
))
```

Initialize a problem with four tuples: a tuple
of `Decision`, a tuple of `Objective`, a tuple of
`Constraint`, and a tuple of `Tagalong`.  Any of these
tuples may have zero size, but not all of them.

For example:

```
from deltamoea import Decision
from deltamoea import Objective
from deltamoea import Constraint
from deltamoea import Tagalong
from deltamoea import Problem
problem = Problem(
    (Decision("decision1", 0.0, 1.0, 0.1),
     Decision("decision2", 0, 50, 16)),
    (Objective("objective1", deltamoea.MINIMIZE),
     Objective("objective2", deltamoea.MAXIMIZE)),
    (Constraint("constraint1", deltamoea.MINIMIZE),
     Constraint("constraint2", deltamoea.MAXIMIZE)),
    (Tagalong("tagalong")))
```

This example defines a problem with two decisions, two
objectives, two constraints, and one tagalong.

### Creating a State Object: `deltamoea.create_moea_state`

Creating a state object is a more involved initialization
routine.

This is the signature of `create_moea_state`:

```
def create_moea_state(problem, **kwargs)
```

#### Positional Arguments

* `problem`: a `deltamoea.Problem`

#### Keyword Arguments

* `ranks`: an `int` indicating how many ranks the
comprehensive archive should contain.  The default is 100.
* `ranksize`: an `int` indicating how large the ranks
should be allowed to grow.  The default is 10,000.
* `float_values`: either `deltamoea.RETAIN` or `deltamoea.DISCARD`.
Determines whether the actual decision variable values
should be retained.  Otherwise only the index of the grid
point is retained.  `DISCARD` is the default.  `RETAIN`
is only needed if you are providing δMOEA with off-grid
decision variable values.  (Perhaps because you are using
local optimization or samples from another source.)
* `random`: a function that generates floating point
numbers on the interval [0,1).  If not specified, δMOEA
uses the Python standard library's `random.random`.
* `randint`: a function that generates integers.  Its
signature should be `randint(a, b)`, where `a` and `b`
are integers specifying the interval on which the integers
should be generated.  `randint` should return numbers on
the interval [a,b].  If not specified, δMOEA uses the
Python standard library's `random.randint`.

There is a tradeoff between `ranks` and `ranksize`.
Problems with many objectives require a smaller number of
large ranks, while problems with few objectives require a
larger number of small ranks.  The default is a compromise
that uses a great deal of space and accommodates a wide
variety of problems.

#### Returns

An initialized `MOEAState`.

#### Example

```
state = deltamoea_create_state(problem, ranks=30)
```

This creates a state object with 30 archive ranks.

### Setting the DOE State: `deltamoea.doe`

δMOEA will perform an initial sample ("design of
experiments", or DOE) before switching over to evolutionary
heuristics.  The `doe` function controls how this sampling
is performed.  The built in experimental designs are not
sophisticated.  Users interested in principled approaches
should investigate saturated fractional factorial designs,
Latin hypercube sampling, quasirandom sampling, and so on.
The built-in initial sampling can be disabled and replaced
with one of these approaches if desired.

#### Positional Arguments

* `state`: a `MOEAState` object

#### Keyword Arguments

* `terminate`: how to terminate the initial sampling.
This can be `CORNERS`, `OFAT`, `CENTERPOINT`, or `COUNT`.
The first three options indicate that the initial sampling
should stop after finishing that step, i.e. after sampling
all the corners of the decision grid, or after sampling
one decision at a time, or after sampling the center point
of the decision space.  `COUNT` indicates that a specified
number of samples should be issued before switching to
evolutionary search.  `COUNT` is the default.
* `count`: an `int`.  If the termination condition is
`COUNT`, this number controls how many samples will
be issued.  Otherwise this argument does nothing.
This defaults to doing as many samples as there are
decision variables.
* `stage`: where to start the initial sampling.  This can
be `CORNERS`, `OFAT`, `CENTERPOINT`, or `RANDOM`.  It
defaults to `RANDOM`.

Taken together, the default keyword arguments specify
an initial random sample of size equal to the number
of decisions.

#### Example

```
from deltamoea import doe
from deltamoea import OFAT
from deltamoea import CENTERPOINT
state = doe(state, terminate=CENTERPOINT, stage=OFAT)
```

This example performs an initial sampling that exercises
each decision individually and then issues a sample for
the centerpoint of the decision space.  To illustrate,
a 5x5 grid for 2 decisions would be sampled as follows:

```
..x..
.....
x.x.x
.....
..x..
```

Here, a period indicates an unsampled grid point and an
x indicates a sampled grid point.

#### Turning Off DOE

To turn off the initial sampling completely, for example
when reusing previous evaluations or performing one's own
initial sampling, set the termination condition to `COUNT`,
set the `count` to 0, and set the `stage` to `RANDOM`:

```
from deltamoea import doe
from deltamoea import COUNT
from deltamoea import RANDOM
state = doe(state, terminate=COUNT, count=0, stage=RANDOM)
```

## Main Loop

δMOEA has two "Main Loop" functions: `deltamoea.get_sample`
and `deltamoea.return_evaluated_individual`.  These functions
are ordinarily called in a main optimization loop.
However, δMOEA does not impose a specific control
structure and these functions may be called on a valid
state object at any time and in any order.

### Sampling: `deltamoea.get_sample`

`get_sample` produces a set of decision variables and an
updated state object.  δMOEA works hard to avoid producing
duplicates, although it is possible that this will happen.

#### Positional Arguments

* `state`: a valid `MOEAState` object

#### Returns

* An `MOEAState` object.
* A `tuple` of `float` values representing a sample on
the decision space.

#### Raises

* `deltamoea.NearExhaustionWarning`: most of the decision space
has been sampled.  It's probably not worth continuing, but
the error can be recovered.
* `deltamoea.TotalExhaustionError`:  The entire decision space
has been sampled.  It's a waste of electricity to continue,
but even this error can be recovered.

Recovery: both exception types have a `state` field which
is a valid `MOEAState`.  Recover by retrieving the `state`
from the exception object and using it as the state going
forward.

#### Example

```
for _ in range(10000):
    try:
        state, dvs = get_sample(state)
    except NearExhaustionWarning as ew:
        print("Nearly Exhausted!  Switch to exhaustive search!")
        state = ew.state
        continue
    except TotalExhaustionError as te:
        print("Totally Exhausted!  Escape!")
        state = te.state
        break
```

### Sorting: `deltamoea.Individual`

To return an evaluation to δMOEA, we must first
construct an `Individual` to represent that evaluation.
An _individual_ is a set of decisions (a _sample_) along
with the objectives, constraints, and tagalongs resulting
from evaluation.

The `Individual` type is defined as follows:

```
Individual = namedtuple("Individual", (
    "decisions",    # tuple of floats
    "objectives",   # tuple of floats
    "constraints",  # tuple of floats
    "tagalongs",    # tuple of floats
))
```

The tuples used to construct an `Individual` may be empty:
for instance, if the problem has only constraints and no
objectives, the `objectives` tuple will have zero length.

### Sorting: `deltamoea.return_evaluated_individual`

`return_evaluated_individual` sorts an evaluated individual
into δMOEA's comprehensive Pareto rank archive.

#### Positional Arguments

* `state`: a valid `MOEAState` object
* `individual`: a `deltamoea.Individual`

#### Returns

* An `MOEAState` object.

#### Example

```
objs, constr, tags = evaluate(dvs)
individual = Individual(dvs, objs, constr, tags)
state = return_evaluated_individual(state, individual)
```

In this example, `dvs` is a tuple of decision variable
values, `objs` is a tuple of objective function values,
`constr` is a tuple of constraint values, and `tags` is
a tuple of tagalong values.  `evaluate` is a function
implementing an optimization model.  The `Individual`
returned must have the same number of decisions,
objectives, constraints, and tagalongs as the `Problem`
used to initialize the state object.

## Termination Conditions

Most MOEAs require the user to specify a termination
condition to the MOEA.  δMOEA leaves the main loop
to the user.  The simplest possible main loop looks
like this:

```
for _ in range(1000):
    state, dvs = get_sample(state)
    objs, constr, tags = evaluate(dvs)
    individual = Individual(dvs, objs, constr, tags)
    state = return_evaluated_individual(state, individual)
```

In this example, we get, evaluate, and return 1000 samples.
It is advisable to handle `NearExhaustionWarning` and
`TotalExhaustionError` to avoid unexpected termination.
(See the documentation for `get_sample`.)

## Extracting Results: `deltamoea.get_iterator`

This function returns an iterator over the individuals in
a rank of δMOEA's Pareto rank archive.

#### Positional Arguments

* `state`: a valid `MOEAState` object
* `rank`: an `int` indicating the desired rank

#### Returns

* A generator function that returns the individuals in
the requested archive rank
 
#### Example

```
for individual in get_iterator(state, 0):
    print(individual)
```

