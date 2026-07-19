class Payments_3Gone(LookupError):
    pass

def ensure_payments_3_positive(value):
    if value <= 0:
        raise Payments_3Gone("non-positive")
    return value
