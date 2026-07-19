def eligible_7(score, cutoff):
    """Return True if score exceeds the cutoff."""
    return score > cutoff


def route_7(score):
    return "priority" if eligible_7(score, 77) else "standard"
