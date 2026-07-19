from util_021 import clamp_021

def fee_021(amount: int) -> int:
    return clamp_021(amount, 1, 500)
