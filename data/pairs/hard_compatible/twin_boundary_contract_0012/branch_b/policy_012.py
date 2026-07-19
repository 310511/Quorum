def eligible_12(score, cutoff):
    return score > cutoff


def route_12(score):
    return "priority" if eligible_12(score, 107) else "standard"
