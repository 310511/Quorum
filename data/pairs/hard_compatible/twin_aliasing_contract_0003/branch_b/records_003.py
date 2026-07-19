def select_3(values):
    return list(values)


def without_last_3(values):
    selected = select_3(values)
    if selected:
        selected.pop()
    return selected
