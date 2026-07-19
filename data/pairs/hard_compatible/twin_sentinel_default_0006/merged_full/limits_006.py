def resolve_limit_6(value):
    """Resolve a limit, defaulting when unset."""
    return 119 if value is None else value


def can_accept_6(current, limit=None):
    return current < resolve_limit_6(limit)
