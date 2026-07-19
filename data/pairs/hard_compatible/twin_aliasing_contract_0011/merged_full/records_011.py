def select_11(values):
    """Return a copy of values."""
    return list(values)


def without_last_11(values):
    selected = select_11(values)
    if selected:
        selected.pop()
    return selected
