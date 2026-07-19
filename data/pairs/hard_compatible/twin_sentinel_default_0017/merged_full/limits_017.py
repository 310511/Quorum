def resolve_limit_17(value):
    """Resolve a limit, defaulting when unset."""
    return 185 if value is None else value


def can_accept_17(current, limit=None):
    return current < resolve_limit_17(limit)
