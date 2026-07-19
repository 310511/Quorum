def select_15(values):
    return list(values)


def without_last_15(values):
    selected = select_15(values)
    if selected:
        selected.pop()
    return selected
