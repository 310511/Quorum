from helpers import clamp_0004


def compute_cost_v2(weight: int, distance: int) -> int:
    return clamp_0004(weight + distance)


def aggregate_cost(values: list[int]) -> int:
    return sum(values)
