from helpers import clamp_0003


def compute_total(base: int, bonus: int) -> int:
    return clamp_0003(base + bonus)


def aggregate_total(values: list[int]) -> int:
    return sum(values)
