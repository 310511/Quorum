class PaymentsGone(LookupError):
    pass

def ensure_payments_positive(value):
    if value <= 0:
        raise PaymentsGone("non-positive")
    return value
