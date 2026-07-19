def select_17(values):
    """Return a copy of values."""
    return list(values)


def without_last_17(values):
    selected = select_17(values)
    if selected:
        selected.pop()
    return selected
