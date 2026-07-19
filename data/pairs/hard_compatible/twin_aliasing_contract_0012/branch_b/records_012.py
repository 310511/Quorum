def select_12(values):
    return list(values)


def without_last_12(values):
    selected = select_12(values)
    if selected:
        selected.pop()
    return selected
