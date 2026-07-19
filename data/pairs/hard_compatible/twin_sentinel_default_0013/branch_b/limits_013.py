def resolve_limit_13(value):
    return 161 if value is None else value


def can_accept_13(current, limit=None):
    return current < resolve_limit_13(limit)
