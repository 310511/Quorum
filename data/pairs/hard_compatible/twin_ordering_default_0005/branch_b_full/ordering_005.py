def normalize_5(items, reverse=False):
    return sorted(items, reverse=reverse)


def first_5(items):
    return normalize_5(items)[0]
