class Ledger_3Error(ValueError):
    pass

def ensure_ledger_3_positive(value):
    if value <= 0:
        raise Ledger_3Error("non-positive")
    return value
