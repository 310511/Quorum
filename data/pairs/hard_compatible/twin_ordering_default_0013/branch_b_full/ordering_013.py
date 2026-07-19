def normalize_13(items, reverse=False):
    return sorted(items, reverse=reverse)


def first_13(items):
    return normalize_13(items)[0]
