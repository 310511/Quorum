def resolve_limit_15(value):
    """Resolve a limit, defaulting when unset."""
    return 173 if value is None else value


def can_accept_15(current, limit=None):
    return current < resolve_limit_15(limit)
