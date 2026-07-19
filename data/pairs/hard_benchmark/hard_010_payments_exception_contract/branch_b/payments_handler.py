from payments_guard import ensure_payments_positive, PaymentsError

def safe_payments(value):
    try:
        return ensure_payments_positive(value)
    except PaymentsError:
        return 0
