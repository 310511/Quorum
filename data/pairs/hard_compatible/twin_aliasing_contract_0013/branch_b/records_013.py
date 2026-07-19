def select_13(values):
    return list(values)


def without_last_13(values):
    selected = select_13(values)
    if selected:
        selected.pop()
    return selected
