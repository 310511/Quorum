def normalize_11(items, reverse=False):
    """Return items sorted according to `reverse`."""
    return sorted(items, reverse=reverse)


def first_11(items):
    return normalize_11(items)[0]
