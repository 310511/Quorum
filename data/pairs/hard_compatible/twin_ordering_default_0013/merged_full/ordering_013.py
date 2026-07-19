def normalize_13(items, reverse=False):
    """Return items sorted according to `reverse`."""
    return sorted(items, reverse=reverse)


def first_13(items):
    return normalize_13(items)[0]
