class Checkout_1Error(ValueError):
    pass

def ensure_checkout_1_positive(value):
    if value <= 0:
        raise Checkout_1Error("non-positive")
    return value
