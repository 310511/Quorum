def normalize_4(items, reverse=False):
    """Return items sorted according to `reverse`."""
    return sorted(items, reverse=reverse)


def first_4(items):
    return normalize_4(items)[0]
