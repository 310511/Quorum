def eligible_13(score, cutoff):
    return score > cutoff


def route_13(score):
    return "priority" if eligible_13(score, 113) else "standard"
