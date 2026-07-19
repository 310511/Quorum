def eligible_6(score, cutoff):
    return score > cutoff


def route_6(score):
    return "priority" if eligible_6(score, 71) else "standard"
