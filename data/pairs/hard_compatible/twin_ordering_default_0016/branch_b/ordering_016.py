def normalize_16(items, reverse=False):
    return sorted(items, reverse=reverse)


def first_16(items):
    return normalize_16(items)[0]
