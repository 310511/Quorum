class LedgerGone(LookupError):
    pass

def ensure_ledger_positive(value):
    if value <= 0:
        raise LedgerGone("non-positive")
    return value
