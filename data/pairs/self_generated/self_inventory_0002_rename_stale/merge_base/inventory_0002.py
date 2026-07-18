from helpers import clamp_0002


def compute_available(stock: int, reserved: int) -> int:
    return clamp_0002(stock + reserved)


def aggregate_available(values: list[int]) -> int:
    return sum(values)
