# Focus on Decision Space

2017-02-14 13:29

UDMOEA attempts to find nondominated points that occupy
as much of the decision space as possible.  This is unusual.
In general, MOEAs focus on occupying as much of the
objective space as possible.  Indeed, since the 1990s,
the trend has been away from a focus on decision space
(diversity maintenance via sharing or niching) and towards the
objective space (diversity maintenance via crowding
distance or epsilons).

We regard this attention as misdirected.  In any real-world
problem, there is a great deal more uncertainty around
objectives than around decisions.  There are two aspects
to uncertainty around objectives.  The first is simple model
uncertainty: no computational model can completely capture
the performance of a physical system, so behavior may not
reflect model predictions.  The second is is uncertainty
around the choice of objectives: any choice of objectives
is provisional until it can be evaluated in the context of
a Pareto approximation.

Decisions, on the other hand, have a much more
appealing case on both counts.  On the first count, model
uncertainty, decisions are much better understood.  In some
cases, as when making discrete decisions, their values
are exact.  In other cases, as when setting a physical
property like length or capacitance, we are dealing with
a quantity that can be determined to a known tolerance.
On the second count, while not completely insensitive to
changes in how a problem is framed, decisions are both
better known and less subject to change than objectives.

