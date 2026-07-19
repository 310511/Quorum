def select_10(values):
    return list(values)


def without_last_10(values):
    selected = select_10(values)
    if selected:
        selected.pop()
    return selected
