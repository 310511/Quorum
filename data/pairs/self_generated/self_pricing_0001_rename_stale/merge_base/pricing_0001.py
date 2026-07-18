from helpers import clamp_0001


def compute_subtotal(price: int, discount: int) -> int:
    return clamp_0001(price + discount)


def aggregate_subtotal(values: list[int]) -> int:
    return sum(values)
