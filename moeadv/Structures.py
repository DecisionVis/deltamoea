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
# Its decisions are index-valued.  Despite having the same
# field names as the Problem, the values in each of the
# tuples are just numbers.
ArchiveIndividual = namedtuple("ArchiveIndividual", (
    "decisions",    # tuple of indices
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

# DOE state:
DOEState = namedtuple("DOEState", (
    "stage",        # CENTERPOINT, OFAT, CORNERS, RANDOM
    "terminate",    # CENTERPOINT, OFAT, CORNERS, COUNT
    "counter",      # int to keep track of where you are in the stage
    "remaining",    # int to keep track of the remaining COUNT
))

# Algorithm state at some point in time.
MOEAState = namedtuple("MOEAState", (
    "problem",             # a Problem
    "archive",             # a tuple of Ranks
    "random",              # real-valued [0,1) RNG
    "randint",             # integer-valued [a, b] RNG
    "doestate",            # a DOEState
))
