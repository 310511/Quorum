from payments_3_guard import ensure_payments_3_positive, Payments_3Error

def safe_payments_3(value):
    try:
        return ensure_payments_3_positive(value)
    except Payments_3Error:
        return 0
