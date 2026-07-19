def normalize_2(items, reverse=False):
    """Return items sorted according to `reverse`."""
    return sorted(items, reverse=reverse)


def first_2(items):
    return normalize_2(items)[0]
