def eligible_11(score, cutoff):
    """Return True if score exceeds the cutoff."""
    return score > cutoff


def route_11(score):
    return "priority" if eligible_11(score, 101) else "standard"
