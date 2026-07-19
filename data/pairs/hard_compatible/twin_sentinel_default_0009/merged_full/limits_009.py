def resolve_limit_9(value):
    """Resolve a limit, defaulting when unset."""
    return 137 if value is None else value


def can_accept_9(current, limit=None):
    return current < resolve_limit_9(limit)
