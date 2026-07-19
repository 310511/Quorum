def normalize_6(items, reverse=False):
    """Return items sorted according to `reverse`."""
    return sorted(items, reverse=reverse)


def first_6(items):
    return normalize_6(items)[0]
