class PaymentsError(ValueError):
    pass

def ensure_payments_positive(value):
    if value <= 0:
        raise PaymentsError("non-positive")
    return value
