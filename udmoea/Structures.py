from collections import namedtuple

# Decision: name(string) lower(float) upper(float) delta(float < upper - lower)
Decision = namedtuple("Decision", ("name", "lower", "upper", "delta"))

# Objective: name(string) sense(MINIMIZE or MAXIMIZE)
Objective = namedtuple("Objective", ("name", "sense"))

# Constraint: name(string) sense(MINIMIZE or MAXIMIZE)
# Constraints are special because they are always relative to 0.
# A MINIMIZE constraint is met if <= 0
# A MAXIMIZE constraint is met if >= 0
Constraint = namedtuple("Constraint", ("name", "sense"))

# Tagalong: allow the user to attach other data to an individual
Tagalong = namedtuple("Tagalong", ("name",))

# Problem: everything the library needs to know about the
# optimization problem
Problem = namedtuple("Problem", (
    "decisions",    # tuple of decisions
    "objectives",   # tuple of objectives
    "constraints",  # tuple of constraints
    "tagalongs",    # tuple of tagalongs
))

# ArchiveIndividual: A member of the archive, for internal use.
# It retains the grid position of each individual.  Optionally
# it retains the actual decision variable values as well, but
# the decisions tuple may be zero-length.
# Despite having the same field names as the Problem,
# the values in each of the tuples are just numbers.
ArchiveIndividual = namedtuple("ArchiveIndividual", (
    "valid",        # bool: whether the individual is valid
    "grid_point",   # tuple of indices
    "decisions",    # tuple of floats
    "objectives",   # tuple of floats
    "constraints",  # tuple of floats
    "tagalongs",    # tuple of floats
))

# Individual: An individual from the user's point of view.
# Its decisions are real-valued.
Individual = namedtuple("Individual", (
    "decisions",    # tuple of floats
    "objectives",   # tuple of floats
    "constraints",  # tuple of floats
    "tagalongs",    # tuple of floats
))

# Rank: a set of individuals, none of which dominates any other
# The Individual type itself will be defined at run-time, when
# the Problem is provided to the library.
Rank = namedtuple("Rank", (
    "individuals",  # list of individuals
    "occupancy"     # number of valid individuals present
))

# DOE state: state of the ongoing DOE
DOEState = namedtuple("DOEState", (
    "stage",        # CENTERPOINT, OFAT, CORNERS, RANDOM, EXHAUSTIVE, EXHAUSTED
    "terminate",    # CENTERPOINT, OFAT, CORNERS, COUNT
    "counter",      # int to keep track of where you are in the stage
    "remaining",    # int to keep track of the remaining COUNT
))

# Axis: an axis of the sampling grid is a tuple of decision
# values for a decision
Axis = tuple
# GridPoint: a tuple of indices into the sampling grid
GridPoint = tuple
# Grid: the definition of the grid
Grid = namedtuple("Grid", (
    "axes",         # a tuple of Axes
    "deltas",       # a tuple of floats (to speed conversions)
    "GridPoint",    # a namedtuple type to use for the grid points
    "Sample",       # a namedtuple type to use for samples in decision space
))

# Issue: a GridPoint, and an outstanding flag indicating whether that
# GridPoint is still outstanding.
Issue = namedtuple("Issue", (
    "grid_point",   # a GridPoint
    "outstanding",  # whether the grid point represents an outstanding sample
))

# Issued: rolling record of issued samples
# The issued_set member is a cheat -- it breaks my
# restriction on dynamic data structures.  This is ok
# because we can do without it in the C version -- it's
# just there to accelerate scans that are slow in the
# first place because we're using Python.
Issued = namedtuple("Issued", (
    "issues",       # a list of Issue
    "index",        # where we should write the next sample
    "issued_set",   # set of outstanding grid points (Python acceleration)
))

# Algorithm state at some point in time.
MOEAState = namedtuple("MOEAState", (
    "problem",             # a Problem
    "float_values",        # RETAIN or DISCARD floating point decision values
    "grid",                # a Grid
    "archive",             # a list of Ranks
    "rank_A",              # an extra Rank, needed for sorting
    "rank_B",              # an extra Rank, needed for sorting
    "issued",              # an Issued structure
    "random",              # real-valued [0,1) RNG
    "randint",             # integer-valued [a, b] RNG
    "doestate",            # a DOEState
))
