from ledger_3_guard import ensure_ledger_3_positive, Ledger_3Error

def safe_ledger_3(value):
    try:
        return ensure_ledger_3_positive(value)
    except Ledger_3Error:
        return 0
