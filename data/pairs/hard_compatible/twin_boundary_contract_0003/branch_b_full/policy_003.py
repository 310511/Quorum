def eligible_3(score, cutoff):
    return score > cutoff


def route_3(score):
    return "priority" if eligible_3(score, 53) else "standard"
