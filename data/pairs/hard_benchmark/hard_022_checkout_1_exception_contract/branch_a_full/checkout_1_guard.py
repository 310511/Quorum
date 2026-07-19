class Checkout_1Gone(LookupError):
    pass

def ensure_checkout_1_positive(value):
    if value <= 0:
        raise Checkout_1Gone("non-positive")
    return value
