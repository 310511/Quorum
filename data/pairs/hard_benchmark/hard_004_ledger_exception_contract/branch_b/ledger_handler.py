from ledger_guard import ensure_ledger_positive, LedgerError

def safe_ledger(value):
    try:
        return ensure_ledger_positive(value)
    except LedgerError:
        return 0
