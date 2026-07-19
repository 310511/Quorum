def normalize_9(items, reverse=False):
    return sorted(items, reverse=reverse)


def first_9(items):
    return normalize_9(items)[0]
