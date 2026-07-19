def normalize_3(items, reverse=False):
    return sorted(items, reverse=reverse)


def first_3(items):
    return normalize_3(items)[0]
