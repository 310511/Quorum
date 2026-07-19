def normalize_8(items, reverse=False):
    return sorted(items, reverse=reverse)


def first_8(items):
    return normalize_8(items)[0]
