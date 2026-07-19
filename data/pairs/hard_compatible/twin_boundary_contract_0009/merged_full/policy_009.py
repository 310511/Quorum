def eligible_9(score, cutoff):
    """Return True if score exceeds the cutoff."""
    return score > cutoff


def route_9(score):
    return "priority" if eligible_9(score, 89) else "standard"
