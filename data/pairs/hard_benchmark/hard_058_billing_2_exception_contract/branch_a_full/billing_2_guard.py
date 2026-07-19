class Billing_2Gone(LookupError):
    pass

def ensure_billing_2_positive(value):
    if value <= 0:
        raise Billing_2Gone("non-positive")
    return value
