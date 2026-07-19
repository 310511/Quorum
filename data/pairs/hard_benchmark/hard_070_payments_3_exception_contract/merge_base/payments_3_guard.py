class Payments_3Error(ValueError):
    pass

def ensure_payments_3_positive(value):
    if value <= 0:
        raise Payments_3Error("non-positive")
    return value
