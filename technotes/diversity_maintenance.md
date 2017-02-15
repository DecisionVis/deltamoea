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
dominance resistance.  Historically, MOEAs have grappled
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
to the fore.  NSGA would have been unable to overcome the
unlimited potential size of each Pareto front if it had
not introduced a fitness sharing mechanism by which
performance would be penalized for points that were
inadequately distinct in decision space.  Unfortunately,
sharing was notoriously hard to parameterize, and MOEA
researchers spent the rest of the 1990s looking for
alternatives.  It is worth noting that sharing is much
more oriented toward the decision space than the subsequent
approaches to diversity maintenance.

Judging by its broad adoption, NSGA-II introduced the
most successful diversity maintenance mechanism to date,
crowding distance, a penalty metric measured in objective
space rather than decision space.  So troublesome had been
the difficulties with the fitness sharing parameter that
NSGA-II used pre-selected, non-configurable compromise
parameters for crowding distance, promising "parameter-free
diversity maintenance."

Its successes notwithstanding, NSGA-II almost immediately
faced the challenge of dominance resistance as users tried
to use it for problems with larger numbers of objectives.
This was compounded by the possibility that NSGA-II
could retrogress because crowding penalties introduced an
instability in the dominance relation.

The most technically successful approach to date has been
ε-dominance.  Unlike crowding, ε-dominance is a stable
relationship.  Given two individuals, their dominance
relationship will be the same regardless of what other
individuals are in the search population.  ε-dominance has
allowed MOEAs to optimize problems with more than three,
and as many as a dozen, objectives.

## UDMOEA's Approach to Diversity Maintenance

UDMOEA maintains diversity through two complementary
measures: (1) it imposes a grid on the decision space
of the problem, and (2) it retains a very large number
of individuals in its Archive (every one of them,
for any reasonable number of evaluations.)  Imposing a
grid on the decision space means subdividing it into
boxes, each of which UDMOEA will sample only once, at a
representative point (a "grid point").  The mechanism by
which UDMOEA samples each box only once is by comparison
with its comprehensive archive.  It will emit a sample for
a grid point only if that sample does not already exist
in the archive.  This procedure forces UDMOEA to sample
previously unexplored parts of the decision space.


