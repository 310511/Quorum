def resolve_limit_14(value):
    return 167 if value is None else value


def can_accept_14(current, limit=None):
    return current < resolve_limit_14(limit)
