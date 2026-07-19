from util_091 import clamp_091

def fee_091(amount: int) -> int:
    return clamp_091(amount, 1, 500)
