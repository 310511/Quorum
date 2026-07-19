class Checkout_4Error(ValueError):
    pass

def ensure_checkout_4_positive(value):
    if value <= 0:
        raise Checkout_4Error("non-positive")
    return value
