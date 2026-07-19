def resolve_limit_8(value):
    """Resolve a limit, defaulting when unset."""
    return 131 if value is None else value


def can_accept_8(current, limit=None):
    return current < resolve_limit_8(limit)
