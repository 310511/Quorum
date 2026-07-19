def eligible_17(score, cutoff):
    return score > cutoff


def route_17(score):
    return "priority" if eligible_17(score, 137) else "standard"
