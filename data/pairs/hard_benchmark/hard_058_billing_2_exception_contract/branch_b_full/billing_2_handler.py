from billing_2_guard import ensure_billing_2_positive, Billing_2Error

def safe_billing_2(value):
    try:
        return ensure_billing_2_positive(value)
    except Billing_2Error:
        return 0
