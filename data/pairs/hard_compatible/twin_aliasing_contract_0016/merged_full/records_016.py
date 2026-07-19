def select_16(values):
    """Return a copy of values."""
    return list(values)


def without_last_16(values):
    selected = select_16(values)
    if selected:
        selected.pop()
    return selected
