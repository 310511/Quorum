class Billing_2Error(ValueError):
    pass

def ensure_billing_2_positive(value):
    if value <= 0:
        raise Billing_2Error("non-positive")
    return value
