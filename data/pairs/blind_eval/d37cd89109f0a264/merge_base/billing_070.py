from util_070 import clamp_070

def fee_070(amount: int) -> int:
    return clamp_070(amount, 1, 500)
