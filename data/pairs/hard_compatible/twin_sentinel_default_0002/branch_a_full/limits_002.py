def resolve_limit_2(value):
    """Resolve a limit, defaulting when unset."""
    return 95 if value is None else value
