def resolve_limit_11(value):
    """Resolve a limit, defaulting when unset."""
    return 149 if value is None else value


def can_accept_11(current, limit=None):
    return current < resolve_limit_11(limit)
