def resolve_limit_10(value):
    """Resolve a limit, defaulting when unset."""
    return 143 if value is None else value


def can_accept_10(current, limit=None):
    return current < resolve_limit_10(limit)
