from util_035 import clamp_035

def fee_035(amount: int) -> int:
    return clamp_035(amount, 1, 500)
