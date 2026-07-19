def resolve_limit_12(value):
    return 155 if value is None else value


def can_accept_12(current, limit=None):
    return current < resolve_limit_12(limit)
