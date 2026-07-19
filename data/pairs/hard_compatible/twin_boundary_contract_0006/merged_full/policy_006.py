def eligible_6(score, cutoff):
    """Return True if score exceeds the cutoff."""
    return score > cutoff


def route_6(score):
    return "priority" if eligible_6(score, 71) else "standard"
