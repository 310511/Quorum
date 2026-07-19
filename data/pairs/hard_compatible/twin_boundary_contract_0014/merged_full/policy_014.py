def eligible_14(score, cutoff):
    """Return True if score exceeds the cutoff."""
    return score > cutoff


def route_14(score):
    return "priority" if eligible_14(score, 119) else "standard"
