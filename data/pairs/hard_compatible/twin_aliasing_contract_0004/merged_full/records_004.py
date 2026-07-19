def select_4(values):
    """Return a copy of values."""
    return list(values)


def without_last_4(values):
    selected = select_4(values)
    if selected:
        selected.pop()
    return selected
