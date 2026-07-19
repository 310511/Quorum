def select_7(values):
    return list(values)


def without_last_7(values):
    selected = select_7(values)
    if selected:
        selected.pop()
    return selected
