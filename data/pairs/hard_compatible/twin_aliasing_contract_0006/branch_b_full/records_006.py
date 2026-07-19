def select_6(values):
    return list(values)


def without_last_6(values):
    selected = select_6(values)
    if selected:
        selected.pop()
    return selected
