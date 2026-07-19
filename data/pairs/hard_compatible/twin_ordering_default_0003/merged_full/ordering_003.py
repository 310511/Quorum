def normalize_3(items, reverse=False):
    """Return items sorted according to `reverse`."""
    return sorted(items, reverse=reverse)


def first_3(items):
    return normalize_3(items)[0]
