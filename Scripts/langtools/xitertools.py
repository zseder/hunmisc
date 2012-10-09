"""Contains methods that in a better world should be in the itertools module."""

def all_partitions(lst):
    """Returns all possible partitionings of a list."""
    length = len(lst)
    for splits in xrange(length):
        for ret in split_list(lst, splits):
            yield ret

def split_list(lst, splits):
    """Splits a list all possible ways with the specified number of splits."""
    if len(lst) <= splits:
        raise ValueError("length {0} <= splits {1}".format(len(lst), splits))

    if splits == 0:
        yield [lst]
    else:
        for i in xrange(len(lst) - splits, 0, -1):
            for rest in split_list(lst[i:], splits - 1):
                ret = [lst[0 : i]]
                ret.extend(rest)
                yield ret

def __split_length(length, splits):
    """
    Splits an integer length all possible ways with the specified number
    of splits.
    """
    if length <= splits:
        raise ValueError("length {0} <= splits {1}".format(length, splits))

    if splits == 0:
        yield [length]
    else:
        for i in xrange(length - splits, 0, -1):
            for rest in __split_length(length - i, splits - 1):
                ret = [i]
                ret.extend(rest)
                yield ret

