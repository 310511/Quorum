def normalize_15(items, reverse=False):
    """Return items sorted according to `reverse`."""
    return sorted(items, reverse=reverse)


def first_15(items):
    return normalize_15(items)[0]
