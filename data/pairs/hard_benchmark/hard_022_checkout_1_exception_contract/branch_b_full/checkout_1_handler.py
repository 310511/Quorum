from checkout_1_guard import ensure_checkout_1_positive, Checkout_1Error

def safe_checkout_1(value):
    try:
        return ensure_checkout_1_positive(value)
    except Checkout_1Error:
        return 0
