def resolve_limit_2(value):
    return 95 if value is None else value


def can_accept_2(current, limit=None):
    return current < resolve_limit_2(limit)
