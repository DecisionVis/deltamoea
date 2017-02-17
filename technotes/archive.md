# Comprehensive Archiving

2017-02-15 08:35

Comprehensive archiving means that UDMOEA does not maintain
an active search population like other MOEAs.  Instead,
UDMOEA archives every evaluation and uses a selection
mechanism to supply evolutionary pressure.

Archiving all, or at least a very large number of,
evaluated individuals is possible only because modern
microcomputers have more main memory by three to four
orders of magnitude than did those available during the
early development of MOEAs in the 1990s.  A basic
assumption held over from that time is that it is
necessary to discard the results of old evaluations
to make room for new.  This assumption no longer holds.

# Archive Structure

The Archive is a large array of individuals, subdivided
into ranks.  Each rank corresponds to a Pareto rank.
By default, UDMOEA uses a large number of large ranks:
100 ranks of 10,000 individuals each.  Each individual
is represented as a grid point, a set of objective values,
a set of constraint values, and a set of tagalong values.

## Archive Size

Here is a back-of-the-envelope calculation of Archive
size:

Let us assume that a reasonably large individual is
represented by 500 numbers.  Assume further that each
of these numbers is a double-precision floating-point
number requiring eight bytes of storage.  Therefore
an individual requires 4000 bytes of storage.  Each
rank therefore requires 40,000,000 bytes of storage,
or about 40 megabytes.  Storing 100 ranks thus requires
4,000,000,000 bytes of storage, or 4 gigabytes.

4 gigabytes is a large but obtainable amount of memory
on a modern workstation.  Furthermore, the Archive
represents the overwhelming bulk of UDMOEA's memory
allocation, and its size is fixed.  The user can
select a rank size or number of ranks suited to the
problem, as well.  Problems with fewer objectives will
likely not require such large ranks, and problems with
more objectives will likely not require so many ranks.

# Scanning

So that UDMOEA will not issue the same sample a second time,
it must scan its Archive.  Since most of UDMOEA's
evolutionary search activity will be in the vicinity of 
Archive rank 0, most duplicates will be found without
scanning a large number of ranks.  However, no sample
will be issued without having scanned all retained
evaluations.  This is an expensive design decision based
on the assumption that model evaluations are even more
expensive than Archive scans and should never be wasted.
The expense of this design can, however, be tuned based on
user tolerance for duplicate model evaluations.  Opting to
retain fewer Pareto ranks will lower the cost of scanning
the Archive.

# Insertion

Since the Archive is structured around Pareto ranks, it
will always be Pareto sorted.  Maintaining that structure
means every insertion causes the Archive to be reordered.
Ordinarily inserting a new individual will kick off a
small cascade as it displaces other individuals from
the rank in which it is nondominated.  These displaced
individuals will then sort into a lower rank, displacing
more individuals into still lower ranks.  This effect
will tend to dissipate in most cases as some displaced
individuals will not displace any further individuals as
they settle into a lower rank.  In the worst case, an
individual will be inserted that dominates the entire
Archive, forcing the entire Archive to be re-sorted.  As
the number of evaluations increases, however, these events
will become vanishingly unlikely.

# Rank Overflow

The default rank size of 10,000 is chosen such that
most problems will never fill a rank with nondominated
individuals.  Nevertheless, it is possible that this
will happen.  If it does, the overflow individuals will be
sorted into the next rank and a warning will be emitted.
While it will be possible for UDMOEA to continue its
multiobjective search in this case, its selection
preference for superior Pareto ranks will disfavor the
part of decision space represented by the individuals that
were forced into an inferior Pareto rank.

# Archive Overflow

If the problem structure results in a large number
of Pareto ranks, UDMOEA will collect the most inferior
individuals in the last rank.  Therefore there will be no
guarantee that the last rank is nondominated with respect
to itself, unlike the other ranks. If the last rank fills
up, UDMOEA will, as a last resort, issue a warning and
begin arbitrarily discarding individuals from the last
rank.  This means that with the default parameterization,
in the worst possible case, UDMOEA will begin discarding
individuals after 10,099 have been inserted in the Archive.

The worst possible case mentioned above is not entirely
unlikely.  Any single-objective optimization problem has
a structure that gives rise to it.  It is likely that the
set of individuals in the Archive for a single-objective
problem have a total ordering, meaning that no rank has a
size larger than one.  Adjusting the `ranks` and `ranksize`
parameters will be necessary for single-objective
optimization problems.

# Off-Grid Samples

Another challenge to comprehensive archiving is the
question of what to do with individuals that were not
evaluated at grid points.  It is possible that the user
has available samples that were not sampled on the same
grid, or on any grid.  There may be multiple individuals
at different places in the same grid box.

UDMOEA's strategy for off-grid individuals is as follows:
permit at most one sample from any grid box in each
Archive rank.  This requires a slight tweak to the
dominance relation.  If two individuals from the same
grid box are otherwise nondominated, the one closer
to the grid point (in index-normalized space) dominates
the other.  In the unlikely circumstance that both
individuals are equidistant from the grid point as well
as being nondominated, one will be demoted to the next
Pareto rank arbitrarily.

