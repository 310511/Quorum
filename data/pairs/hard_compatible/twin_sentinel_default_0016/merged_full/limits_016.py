def resolve_limit_16(value):
    """Resolve a limit, defaulting when unset."""
    return 179 if value is None else value


def can_accept_16(current, limit=None):
    return current < resolve_limit_16(limit)
