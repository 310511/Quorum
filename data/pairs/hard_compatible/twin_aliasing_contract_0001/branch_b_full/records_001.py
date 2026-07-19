def select_1(values):
    return list(values)


def without_last_1(values):
    selected = select_1(values)
    if selected:
        selected.pop()
    return selected
