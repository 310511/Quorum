class Shipping_2Gone(LookupError):
    pass

def ensure_shipping_2_positive(value):
    if value <= 0:
        raise Shipping_2Gone("non-positive")
    return value
