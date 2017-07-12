# δMOEA API

(C) 2017 [DecisionVis LLC](http://www.decisionvis.com)

## The State Object: `dmoea.MOEAState`

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

### Preparing a Problem: `dmoea.Decision`

```
Decision = namedtuple("Decision", ("name", "lower", "upper", "delta"))
```

To define a `Decision`, initialize its fields.  For example:

```
decision1 = Decision("decision1", 0.0, 1.0, 0.1)
decision2 = Decision("decision2", 0, 50, 16)
```

`delta` is the grid spacing for that decision.  `decision1`
in this example will be sampled on 11 grid points: 0.0,
0.1, ... 1.0.  `decision2` will be sampled on 4 grid points:
1, 17, 33, and 49.  (δMOEA will split the difference if
the spacing does not evenly divide the range.)

### Preparing a Problem: `dmoea.Objective`

```
Objective = namedtuple("Objective", ("name", "sense"))
```

To define an `Objective`, initialize its fields.  For example:

```
objective1 = Objective("objective1", dmoea.MINIMIZE)
objective2 = Objective("objective2", dmoea.MAXIMIZE)
```

Valid values for `sense` are `dmoea.MINIMIZE` and
`dmoea.MAXIMIZE`.

### Preparing a Problem: `dmoea.Constraint`

```
Constraint = namedtuple("Constraint", ("name", "sense"))
```

To define a `Constraint`, initialize its fields.  For example:

```
constraint1 = Constraint("constraint1", dmoea.MINIMIZE)
constraint2 = Constraint("constraint2", dmoea.MAXIMIZE)
```

Constraints, if defined, preempt objectives.  Minimization
constraints are considered satisfied when less than
or equal to zero, while maximization constraints
must be greater than or equal to zero.  δMOEA only
considers objectives when comparing two individuals
if both individuals satisfy all of their constraints.
Otherwise δMOEA compares their constraints.

### Preparing a Problem: `dmoea.Tagalong`

```
Tagalong = namedtuple("Tagalong", ("name",))
```

A tagalong makes it possible to store a value for later
use.  It has no role in optimization other than to
increase how much RAM δMOEA uses.

### Preparing a Problem: `dmoea.Problem`

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
problem = Problem(
    (Decision("decision1", 0.0, 1.0, 0.1),
     Decision("decision2", 0, 50, 16)),
    (Objective("objective1", dmoea.MINIMIZE),
     Objective("objective2", dmoea.MAXIMIZE)),
    (Constraint("constraint1", dmoea.MINIMIZE),
     Constraint("constraint2", dmoea.MAXIMIZE)),
    (Tagalong("tagalong")))
```

This example defines a problem with two decisions, two
objectives, two constraints, and one tagalong.

### Creating a State Object: `dmoea.create_moea_state`

Creating a state object is a more involved initialization
routine.

```
def create_moea_state(problem, **kwargs)
```

#### Positional Arguments

* `problem`: a `dmoea.Problem`

#### Keyword Arguments

* `ranks`: an `int` indicating how many ranks the
comprehensive archive should contain.  The default is 100.
* `ranksize`: an `int` indicating how large the ranks
should be allowed to grow.  The default is 10,000.
* `float_values`: either `dmoea.RETAIN` or `dmoea.DISCARD`.
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
state = dmoea_create_state(problem, ranks=30)
```

This creates a state object with 30 archive ranks.

## Main Loop

δMOEA has two "Main Loop" functions: `dmoea.get_sample`
and `dmoea.return_evaluated_individual`.  These functions
are ordinarily called in a main optimization loop.
However, δMOEA does not impose a specific control
structure and these functions may be called on a valid
state object at any time and in any order.

### Sampling: `dmoea.get_sample`

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

* `dmoea.NearExhaustionWarning`: most of the decision space
has been sampled.  It's probably not worth continuing, but
the error can be recovered.
* `dmoea.TotalExhaustionError`:  The entire decision space
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

### Sorting: `dmoea.return_evaluated_individual`

`return_evaluated_individual` sorts an evaluated individual
into δMOEA's comprehensive Pareto rank archive.

#### Positional Arguments

* `state`: a valid `MOEAState` object
* `individual`: a `dmoea.Individual`

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

## The Archive

