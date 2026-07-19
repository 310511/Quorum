def resolve_limit_3(value):
    """Resolve a limit, defaulting when unset."""
    return 101 if value is None else value


def can_accept_3(current, limit=None):
    return current < resolve_limit_3(limit)
