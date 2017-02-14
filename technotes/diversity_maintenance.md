# Diversity Maintenance

2017-02-14 13:31

Diversity maintenance refers to the challenge of
maintaining a population whose members are adequately
different from one another, so that the results presented
to the algorithm's user are distinct enough to make
decisions about.  This definition is somewhat hazy.  After
all, what is "adequately different?"  Furthermore, it is
as much a rationalization as it is a definition.  The
fundamental reason for diversity maintenance is that there
is no limit on the number of points in a tradeoff.  Even
a two-dimensional tradeoff may be populated by an unlimited
number of points.

When moving to problems with more objectives, these infinities
expand geometrically, a problem the literature refers to as
"dominance resistance."  Historically, MOEAs have grappled
with the challenge of maintaining an adequate subset of the 
points in a Pareto approximation without having that Pareto
approximation explode in size.

## Background:  Current Approaches to Diversity Maintenance

For practical purposes, the history of multiobjective
evolutionary algorithms dates back to NSGA.  Schaffer's
VEGA predates it, but does not appear to have gained
practical application.  The breakthrough in NSGA is
the nondomination sorting that gives it its name.  Rather
evaluating objectives individually or attempting to
aggregate them, NSGA uses Pareto ranking as a fitness
function.

This breakthrough, however, brought diversity maintenance
to the fore.  NSGA would have remained a curiosity if
it had not introduced a "fitness sharing" mechanism by
which performance would be penalized for points that
were inadequately distinct in decision space.  Unfortunately,
sharing was notoriously hard to parameterize.  It is worth
noting that sharing is much more oriented toward the decision
space than the subsequent approaches to diversity maintenance.



