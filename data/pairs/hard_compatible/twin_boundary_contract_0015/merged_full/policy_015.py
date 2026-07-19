def eligible_15(score, cutoff):
    """Return True if score exceeds the cutoff."""
    return score > cutoff


def route_15(score):
    return "priority" if eligible_15(score, 125) else "standard"
