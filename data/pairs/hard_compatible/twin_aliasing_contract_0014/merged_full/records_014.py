def select_14(values):
    """Return a copy of values."""
    return list(values)


def without_last_14(values):
    selected = select_14(values)
    if selected:
        selected.pop()
    return selected
