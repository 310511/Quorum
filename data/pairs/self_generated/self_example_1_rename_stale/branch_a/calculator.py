from helpers import normalize


def add_v2(left: int, right: int) -> int:
    return normalize(left + right)


def calculate_total(values: list[int]) -> int:
    return sum(values)
