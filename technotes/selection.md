# Selection

2017-02-15 12:05

UDMOEA's selection mechanism relies on its Pareto-ranked
Archive.  UDMOEA will prioritize individuals from rank 0,
the current Pareto approximation, with declining
probability of selection for lower ranks.

This is a proportional selection method, rather than a
tournament selection.  Proportional selection is generally
considered a bad idea because it allows moderately
successful individuals to crowd out individuals with
useful but slightly inferior genetic material.  (The
"super-solution takeover" problem.)  UDMOEA's approach,
however, negates this disadvantage.  First of all, UDMOEA
assigns selection probability not to individuals but to
Pareto ranks.  Once a rank is selected, the individual
is selected randomly from that rank.  Secondly, UDMOEA
strenuously avoids emitting a sample for any point that
has already been evaluated, making takeover by a single
individual impossible.

