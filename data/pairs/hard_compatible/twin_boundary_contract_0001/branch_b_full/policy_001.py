def eligible_1(score, cutoff):
    return score > cutoff


def route_1(score):
    return "priority" if eligible_1(score, 41) else "standard"
