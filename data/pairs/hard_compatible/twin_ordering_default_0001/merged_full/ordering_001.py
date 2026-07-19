def normalize_1(items, reverse=False):
    """Return items sorted according to `reverse`."""
    return sorted(items, reverse=reverse)


def first_1(items):
    return normalize_1(items)[0]
