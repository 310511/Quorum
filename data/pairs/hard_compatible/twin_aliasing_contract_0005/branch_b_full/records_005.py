def select_5(values):
    return list(values)


def without_last_5(values):
    selected = select_5(values)
    if selected:
        selected.pop()
    return selected
