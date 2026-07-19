def resolve_limit_4(value):
    return 107 if value is None else value


def can_accept_4(current, limit=None):
    return current < resolve_limit_4(limit)
