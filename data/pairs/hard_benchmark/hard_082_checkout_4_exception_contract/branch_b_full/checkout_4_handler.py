from checkout_4_guard import ensure_checkout_4_positive, Checkout_4Error

def safe_checkout_4(value):
    try:
        return ensure_checkout_4_positive(value)
    except Checkout_4Error:
        return 0
