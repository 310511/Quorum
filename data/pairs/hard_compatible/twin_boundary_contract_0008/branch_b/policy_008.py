def eligible_8(score, cutoff):
    return score > cutoff


def route_8(score):
    return "priority" if eligible_8(score, 83) else "standard"
