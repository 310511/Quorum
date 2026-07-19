def normalize_17(items, reverse=False):
    """Return items sorted according to `reverse`."""
    return sorted(items, reverse=reverse)


def first_17(items):
    return normalize_17(items)[0]
