def select_8(values):
    return list(values)


def without_last_8(values):
    selected = select_8(values)
    if selected:
        selected.pop()
    return selected
