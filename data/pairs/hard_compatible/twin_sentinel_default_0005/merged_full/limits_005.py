def resolve_limit_5(value):
    """Resolve a limit, defaulting when unset."""
    return 113 if value is None else value


def can_accept_5(current, limit=None):
    return current < resolve_limit_5(limit)
