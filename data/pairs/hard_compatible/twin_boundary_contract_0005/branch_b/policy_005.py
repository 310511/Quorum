def eligible_5(score, cutoff):
    return score > cutoff


def route_5(score):
    return "priority" if eligible_5(score, 65) else "standard"
