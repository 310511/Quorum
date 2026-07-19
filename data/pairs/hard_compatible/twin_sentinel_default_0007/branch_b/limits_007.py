def resolve_limit_7(value):
    return 125 if value is None else value


def can_accept_7(current, limit=None):
    return current < resolve_limit_7(limit)
