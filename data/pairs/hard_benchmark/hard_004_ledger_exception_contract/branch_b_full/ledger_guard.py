class LedgerError(ValueError):
    pass

def ensure_ledger_positive(value):
    if value <= 0:
        raise LedgerError("non-positive")
    return value
