def normalize_5(items, reverse=False):
    """Return items sorted according to `reverse`."""
    return sorted(items, reverse=reverse)


def first_5(items):
    return normalize_5(items)[0]
