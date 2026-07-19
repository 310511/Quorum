def eligible_9(score, cutoff):
    return score > cutoff


def route_9(score):
    return "priority" if eligible_9(score, 89) else "standard"
