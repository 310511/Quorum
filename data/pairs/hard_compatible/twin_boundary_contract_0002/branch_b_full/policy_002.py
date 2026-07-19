def eligible_2(score, cutoff):
    return score > cutoff


def route_2(score):
    return "priority" if eligible_2(score, 47) else "standard"
