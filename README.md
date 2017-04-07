# δMOEA: A Multi-Objective Evolutionary Algorithm

δMOEA is a multi-objective evolutionary algorithm (MOEA),
with the following well-established algorithmic elements:

* steady-state evaluation
* uniform mutation
* simulated binary crossover
* nondomination sorting

In addition, δMOEA does some things that no other known
MOEA does:

* Uses real-valued decision variables, but produces samples
only at points on a user-specified grid.
* Retains a comprehensive Pareto-ranked archive of (almost)
every evaluated individual.
* (Almost) never suggests resampling the same grid point.
* Determines selection probability based on Pareto rank
in the comprehensive archive.

Also, δMOEA is designed for user convenience.  The key
user-friendly feature is its asynchronous evaluation model.
The default model for MOEAs is for the user to make a
single call to the MOEA, providing it with an evaluation
callback that must conform to the MOEA's expectations of
what an evaluation function does.  This rigid approach
limits the user's ability to supply extra evaluated
individuals, to establish termination conditions, and to
parallelize evaluation.  In addition, it requires
surrendering control of program execution to the MOEA.

δMOEA's asynchronous evaluation model works differently,
putting the user in control of evaluation.  Instead of one
`optimize` function, δMOEA provides two: `get_sample`
and `return_evaluated_individual`.  This split means that
the user can:

* choose not to evaluate a particular sample
* return evaluations out of order
* return evaluations other than those suggested by the
algorithm, such as evaluations from previous optimization
runs

Furthermore, although δMOEA only suggests samples on grid
points, it will accept evaluations from anywhere in the
decision space.

# Copyright

(C) 2017 DecisionVis LLC

# License

This Python implementation of δMOEA is available under
the GNU General Public License, Version 3.
