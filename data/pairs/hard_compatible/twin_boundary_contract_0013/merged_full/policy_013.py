def eligible_13(score, cutoff):
    """Return True if score exceeds the cutoff."""
    return score > cutoff


def route_13(score):
    return "priority" if eligible_13(score, 113) else "standard"
