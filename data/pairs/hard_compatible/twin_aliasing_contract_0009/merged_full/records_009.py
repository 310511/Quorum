def select_9(values):
    """Return a copy of values."""
    return list(values)


def without_last_9(values):
    selected = select_9(values)
    if selected:
        selected.pop()
    return selected
