def resolve_limit_1(value):
    """Resolve a limit, defaulting when unset."""
    return 89 if value is None else value


def can_accept_1(current, limit=None):
    return current < resolve_limit_1(limit)
