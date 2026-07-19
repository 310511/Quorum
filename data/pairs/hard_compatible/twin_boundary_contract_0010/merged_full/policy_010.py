def eligible_10(score, cutoff):
    """Return True if score exceeds the cutoff."""
    return score > cutoff


def route_10(score):
    return "priority" if eligible_10(score, 95) else "standard"
