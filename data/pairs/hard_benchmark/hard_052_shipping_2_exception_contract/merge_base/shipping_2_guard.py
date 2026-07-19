class Shipping_2Error(ValueError):
    pass

def ensure_shipping_2_positive(value):
    if value <= 0:
        raise Shipping_2Error("non-positive")
    return value
