def select_13(values):
    """Return a copy of values."""
    return list(values)


def without_last_13(values):
    selected = select_13(values)
    if selected:
        selected.pop()
    return selected
