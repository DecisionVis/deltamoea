def sort_into_archive(state, archive_individual):
    archive = state.archive

    rank_A = state.rank_A._replace(occupancy=0)
    rank_B = state.rank_B._replace(occupancy=0)

    # rank A will always be the one we're sorting into
    # the next archive rank, and rank B will be the
    # recipient of displaced individuals.
    rank_A.individuals[0] = archive_individual
    rank_A = rank_A._replace(occupancy=1)

    rank_into = 0
    # loop over archive ranks
    while rank_A.occupancy > 0:
        into = archive[rank_into]
        print("----")
        print("before: rank {}".format(rank_into))
        _print_rank(into)
        print("before: rank_A")
        _print_rank(rank_A)
        print("before: rank_B")
        _print_rank(rank_B)
        # loop over rank A
        a_remaining = rank_A.occupancy
        for ai, a_ind in enumerate(rank_A.individuals):
            print("processing {} from rank A: {}".format(ai, a_ind))
            if a_remaining <= 0:
                break
            if not a_ind.valid:
                continue
            a_remaining -= 1
            # loop over rank being sorted into
            i_remaining = into.occupancy
            for ii, i_ind in enumerate(into.individuals):
                if i_remaining <= 0:
                    break
                if not i_ind.valid:
                    continue
                i_remaining -= 1
                dominance = _compare(state.problem, a_ind, i_ind)
                # invalidate the dominated individual 
                # insert it into rank_B
                # adjust rank occupancy
                if dominance == LEFT_DOMINATES:
                    rank_B.individuals[rank_B.occupancy] = i_ind
                    rank_B._replace(occupancy=rank_B.occupancy + 1)
                    into.individuals[ii] = i_ind._replace(valid=False)
                    into._replace(occupancy=into.occupancy - 1)
                elif dominance == RIGHT_DOMINATES:
                    rank_B.individuals[rank_B.occupancy] = a_ind
                    rank_B._replace(occupancy=rank_B.occupancy + 1)
                    rank_A.individuals[ai] = a_ind._replace(valid=False)
                    rank_A._replace(occupancy=rank_A.occupancy - 1)
                    # break if rank A individual was dominated and go
                    # to next rank A individual
                    break
        # insert valid individuals from rank A in "into"
        into, rank_A = fill_rank_from_rank(into, rank_A)

        print("after fill: rank {}".format(rank_into))
        _print_rank(into)
        print("after fill: rank_A")
        _print_rank(rank_A)
        print("after fill: rank_B")
        _print_rank(rank_B)

        # insert overflow in rank B
        rank_B, rank_A = fill_rank_from_rank(rank_B, rank_A)

        print("after overflow: rank {}".format(rank_into))
        _print_rank(into)
        print("after overflow: rank_A")
        _print_rank(rank_A)
        print("after overflow: rank_B")
        _print_rank(rank_B)

        # swap rank A and rank B
        rank_B, rank_A = rank_A, rank_B
        # update the archive
        archive[rank_into] = into

        print("after: rank {}".format(rank_into))
        _print_rank(into)
        print("after: rank_A")
        _print_rank(rank_A)
        print("after: rank_B")
        _print_rank(rank_B)

        if rank_A.occupancy == 0:
            break

    state = state._replace(
        rank_A=rank_A,
        rank_B=rank_B,
        archive=archive)

    return state

def _print_rank(rank):
    print("occupancy {}".format(rank.occupancy))
    print("valid {}".format(sum((1 for i in rank.individuals if i.valid))))
    ii = 0
    valid = 0
    while valid < rank.occupancy and ii < len(rank.individuals):
        print(rank.individuals[ii])
        if rank.individuals[ii].valid:
            valid += 1
        ii += 1

def fill_rank_from_rank(destination, source):
    di = 0
    for si, s_ind in enumerate(source.individuals):
        if source.occupancy <= 0:
            break
        if not s_ind.valid:
            continue
        if destination.occupancy >= len(destination.individuals):
            break
        while di < len(destination.individuals):
            if destination.individuals[di].valid:
                di += 1
            else:
                destination.individuals[di] = s_ind
                destination._replace(occupancy=destination.occupancy + 1)
                source.individuals[si] = s_ind._replace(valid=False)
                source._replace(occupancy=source.occupancy - 1)
        if di >= len(destination.individuals):
            break
    return destination, source
