def eligible_4(score, cutoff):
    return score > cutoff


def route_4(score):
    return "priority" if eligible_4(score, 59) else "standard"
