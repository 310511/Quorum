def eligible_16(score, cutoff):
    """Return True if score exceeds the cutoff."""
    return score > cutoff


def route_16(score):
    return "priority" if eligible_16(score, 131) else "standard"
