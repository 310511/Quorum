def normalize_12(items, reverse=False):
    """Return items sorted according to `reverse`."""
    return sorted(items, reverse=reverse)


def first_12(items):
    return normalize_12(items)[0]
