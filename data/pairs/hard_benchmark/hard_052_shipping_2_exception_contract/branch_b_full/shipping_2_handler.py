from shipping_2_guard import ensure_shipping_2_positive, Shipping_2Error

def safe_shipping_2(value):
    try:
        return ensure_shipping_2_positive(value)
    except Shipping_2Error:
        return 0
