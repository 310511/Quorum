def eligible_16(score, cutoff):
    return score > cutoff


def route_16(score):
    return "priority" if eligible_16(score, 131) else "standard"
