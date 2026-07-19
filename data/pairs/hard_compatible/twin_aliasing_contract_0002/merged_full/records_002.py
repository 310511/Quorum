def select_2(values):
    """Return a copy of values."""
    return list(values)


def without_last_2(values):
    selected = select_2(values)
    if selected:
        selected.pop()
    return selected
