# Evaluation Model

2017-02-15 08:36

## Background

The conventional API for a black-box optimizer has a few
setup, configuration, and information retrieval methods,
and a single main method with a signature that looks like
this:

```
optimized_set = optimize(evaluation_function, options)
```

Where the evaluation function must have a signature
like this:

```
objectives and constraints = evaluation_function(decisions)
```

This design presents the optimization run as if it were
a reasonably fast operation producing a result that would
be used in the context of a larger program.  In general,
however, MOEA runs take a significant amount of time,
and this means that any program that does an MOEA run
must surrender control to the MOEA library for an
indefinite amount of time.  As a result, programs that
use MOEAs must be mostly about those MOEAs, rather than
about the problem being addressed.

Furthermore, the requirement that an evaluation function
conform to a particular signature forces users into
awkward design decisions, like adding side-effects to the
evaluation function to capture additional information that
would otherwise be lost.  The fact that these side-effects
could take a significant amount of time or encounter an
error condition presents a further complication that must
be designed around.

## δMOEA Does Not Have A Main Loop

Inside the `optimize` function provided by a conventional
MOEA library, there is a main loop that calls the 
`evaluation_function` repeatedly.  δMOEA has no such main
loop.  Instead, of one `optimize` function, δMOEA presents
two functions that may be called any number of times in
any order: `return_evaluated_individual` and `get_sample`.

`get_sample` requests a set of decision variables from
δMOEA.  What is to be done with these decision variables
is entirely up to the user.  `return_evaluated_individual`
provides δMOEA with a set of decision variables,
objectives, constraints, and tagalong variables
corresponding to one model evaluation.  This de-coupled
design allows the user to provide δMOEA with information
from previous model runs, whether they originated in
initial model exploration, a designed experiment, or a
previous optimization run.  Furthermore, it allows complex
scenarios like local optimization, out-of-order
evaluation, and injection of user-suggested designs.

Despite supporting much more complex uses, writing a
simple main loop for δMOEA is no more complicated than
an invocation of the traditional `optimize` function,
especially considering that it is not necessary to
conform to the `evaluation_function` signature, which
usually requires writing a wrapper function.  A simple
main loop looks like this:

```
until termination condition is met:
    decisions = get_sample()
    model_inputs = input_transformation(decisions)
    model_outputs = evaluate(model_inputs)
    objectives, constraints, and tagalongs = output_transformation(model_outputs)
    return_evaluated_individual(decisions, objectives, constraints, tagalongs)
```

The `input_transformation` and `output_transformation`
functions are optional, and supplied by the user.
They decouple the evaluation function, which may be part
of some other analysis library written for some other
purpose than optimization, from the optimizer.  If the
user already has an `evaluation_function` written for
use with some other MOEA, the main loop becomes even
simpler:

```
until termination condition is met:
    decisions = get_sample()
    objectives, constraints = evaluation_function(decisions)
    return_evaluated_individual(decisions, objectives, constraints, empty_list)
```

## Tagalongs

The pseudocode above includes a component upon which we
have not yet remarked: tagalongs.  Tagalongs are data
resulting from an evaluation, but unlike objectives and
constraints they have no role to play in optimization.
In general their role for the user is to _**preserve enough
information about a model evaluation to make repeating
that evaluation unnecessary in the future.**_  While the user
could store tagalongs offline instead (and should do so
for large or complicated cases), allowing δMOEA to handle
a reasonable amount of tagalong data in its Archive is a
powerful convenience feature.


