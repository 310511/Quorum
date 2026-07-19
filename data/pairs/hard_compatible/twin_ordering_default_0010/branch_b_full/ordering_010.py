def normalize_10(items, reverse=False):
    return sorted(items, reverse=reverse)


def first_10(items):
    return normalize_10(items)[0]
