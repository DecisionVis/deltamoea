# DOEState stages
from .Constants import CENTERPOINT
from .Constants import OFAT
from .Constants import CORNERS
from .Constants import RANDOM
from .Constants import EXHAUSTIVE
from .Constants import EXHAUSTED

class NearExhaustionWarning(Exception):
    def __init__(self, state, *args, **kwargs):
        super(NearExhaustionWarning, self).__init__(*args, **kwargs)
        self.state = state

class TotalExhaustionError(Exception):
    def __init__(self, state, *args, **kwargs):
        super(TotalExhaustionError, self).__init__(*args, **kwargs)
        self.state = state

def _dummy_grid_index(grid):
    """ generator function, placeholder for selection and
    variation operators, and DOE, just returns all grid
    points in no particularly good order. """
    index = grid.GridPoint(*(0 for _ in grid.axes))
    while True:
        yield index
        new_index = list()
        overflow = True
        # treat first index as least significant because
        # it's easiest that way
        for ii, axis in zip(index, grid.axes):
            if overflow:
                if ii+1 < len(axis):
                    new_index.append(ii+1)
                    overflow = False
                else:
                    new_index.append(0)
                    overflow = True
            else:
                new_index.append(ii)
        if overflow:
            raise StopIteration()
        index = grid.GridPoint(*new_index)

dgs = None
def _sample_dummy_grid(state):
    # bootstrapping the algorithm: for now use grid sampling as
    # a placeholder
    global dgs
    if dgs is None:
        dgs = _dummy_grid_index(state.grid)
    grid_point = next(dgs)
    return state, grid_point

def is_duplicate(state, grid_point):
    if grid_point in state.issued.grid_points:
        return True
    return False

def doe_next(state):
    """
    state (MOEAstate)

    Return the next DOE grid point and update state accordingly.
    Will raise an exception if random sampling is having
    trouble finding a free grid point.
    Will raise another exception if a full grid sweep is
    unable to find a free grid point.  Users would be well
    advised to stop after the first exception!  After the
    second exception, we have to start duplicating samples.
    """
    doestate = state.doestate
    stage = doestate.stage
    grid = state.grid
    duplicated = True
    duplicates_generated = 0
    while duplicated:
        if stage == CENTERPOINT:
            grid_point = grid.GridPoint(*(len(a) // 2 for a in grid.axes))
            doestate = doestate._replace(stage=OFAT, counter=0)
        elif stage == OFAT:
            indices = [len(a) // 2 for a in grid.axes]
            counter = doestate.counter
            axis_index = counter // 2 # two points per axis
            axis = grid.axes[axis_index]
            if counter % 2 == 0:
                # low side sample
                indices[axis_index] = 0
            else:
                # high side sample
                indices[axis_index] = len(axis) - 1
            grid_point = grid.GridPoint(*indices)
            advanced_counter = counter + 1
            if advanced_counter // 2 >= len(grid.axes):
                doestate = doestate._replace(stage=CORNERS, counter=0)
            else:
                doestate = doestate._replace(counter=advanced_counter)
        elif stage == CORNERS:
            # Treat the counter like a bitvector, where 0 means low and 1
            # means high.  Because it's easy to write this way, treat
            # axis 0 as the LSB.
            indices = list()
            for ii, axis in enumerate(grid.axes):
                bit = (doestate.counter >> ii) & 1
                if bit == 0:
                    indices.append(0)
                else:
                    indices.append(len(axis) - 1)
            grid_point = grid.GridPoint(*indices)
            advanced_counter = doestate.counter + 1
            if advanced_counter >= 2 ** len(grid.axes):
                doestate = doestate._replace(stage=RANDOM, counter=0)
            else:
                doestate = doestate._replace(counter=advanced_counter)
        elif stage in (RANDOM, EXHAUSTED):
            grid_point = grid.GridPoint(
                *(state.randint(0, len(a) - 1) for a in grid.axes))
            # transition out of RANDOM is if we have too many failures
            doestate = doestate._replace(counter=doestate.counter + 1)
        elif stage == EXHAUSTIVE:
            # Decompose the counter into indices, again treating axis
            # 0 as the least significant because it's easy to write.
            # This also takes advantage of the fact that Python has
            # bignums.  In C we need to check overflow,
            # although if we overflow 2 ** 63 - 1, that means
            # we've sampled almost 1e19 grid points.  So good
            # for us, if we trip over that condition!
            indices = list()
            counter = doestate.counter
            total_points = 1
            for axis in grid.axes:
                alen = len(axis)
                total_points = total_points * alen # mind overflow here!
                indices.append(counter % alen)
                counter = counter // alen
            advanced_counter = doestate.counter + 1
            if advanced_counter >= total_points:
                doestate = doestate._replace(stage=EXHAUSTED, counter=0)
                state = state._replace(doestate=doestate)
                raise TotalExhaustionError(state)
            else:
                doestate = doestate._replace(counter=advanced_counter)
        if stage == EXHAUSTED:
            # No point in wasting time on a duplicate check, and
            # if we're exhausted the loop condition will remain true
            # forever.
            break
        duplicated = is_duplicate(state, grid_point)
        if duplicated and stage == RANDOM:
            duplicates_generated += 1
            # How hard do we want to try here?  This says if the space
            # is more than 99.9% sampled on average we should move over
            # to exhaustive search.
            if duplicates_generated > 1000:
                doestate = doestate._replace(stage=EXHAUSTIVE)
                state = state._replace(doestate=doestate)
                raise NearExhaustionWarning(state)
    state = state._replace(doestate=doestate)
    #state, sample = _sample_dummy_grid(state)
    return state, grid_point

def evolve(state):
    raise StopIteration()
    state, grid_point = _sample_dummy_grid(state)
    return state, grid_point

