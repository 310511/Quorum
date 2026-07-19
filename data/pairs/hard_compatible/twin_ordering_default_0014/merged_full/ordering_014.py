def normalize_14(items, reverse=False):
    """Return items sorted according to `reverse`."""
    return sorted(items, reverse=reverse)


def first_14(items):
    return normalize_14(items)[0]
