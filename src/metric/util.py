def apply_at_indexes(func, elements, indexes):
    ret = [(func(e) if i in indexes else e) for (i, e) in enumerate(elements)]
    return ret


def replace_at_indexes(sequence, indexes, e):
    return apply_at_indexes(lambda x: e, sequence, indexes)


def map_at_indexes(sequence, indexes, d):
    return apply_at_indexes(lambda x: d[x], sequence, indexes)
