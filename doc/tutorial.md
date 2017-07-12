# δMOEA Tutorial

(C) 2017 [DecisionVis LLC](http://www.decisionvis.com)

This is an outline of the tutorial we intend to write for δMOEA.

## Initialization

Defining decisions, objectives, constraints, and tagalongs.

Setting up a problem.

Creating an initial state object.

## Sampling

How to call `get_sample`.

It's not necessary to return any evaluations.

## Sorting

How to call `return_evaluated_individual`.

It's not necessary to request any samples.

## Printing Archive Contents

How to use the iterator functions to get an archive rank.

## Main Loop

Put `get_sample` together with
`return_evaluated_individual`, repeat until satisfied.

## Pre-seeding

Call `return_evaluated_individual` to load up the archive
with evaluations.

## Using Tagalongs

Demonstrate with NFE.

## Printing Runtime Data

Show the evolving rank 0 with individual age.

## Local Optimization

Use RETAIN for `float_disposal`.  Keep other info in
tagalongs as needed.

## Changing Optimization Model

Show how the optimization model can be changed and the
evaluations reused.

