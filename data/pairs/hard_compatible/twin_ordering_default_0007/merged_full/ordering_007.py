def normalize_7(items, reverse=False):
    """Return items sorted according to `reverse`."""
    return sorted(items, reverse=reverse)


def first_7(items):
    return normalize_7(items)[0]
