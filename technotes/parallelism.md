# Parallelism

2017-02-15 11:57

Because UDMOEA does not impose a main loop on the
optimization run, and because it can accept out-of-order
evaluations, the user may overlay any parallelization
strategy on top of UDMOEA, or opt not to parallelize UDMOEA
at all.  This can scale from doing evaluations in threads
all the way to submitting jobs to a TORQUE queue on a big
MPI cluster.  The case in which this does not work well is
when many very fast evaluations can be done in parallel.

When many very fast evaluations can be done in parallel, the
overhead of scanning and sorting the archive will become
a bottleneck.  In this case, users would be better served
to pipe a grid scan into a Pareto filter, than to run
UDMOEA.

