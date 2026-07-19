class Checkout_4Gone(LookupError):
    pass

def ensure_checkout_4_positive(value):
    if value <= 0:
        raise Checkout_4Gone("non-positive")
    return value
