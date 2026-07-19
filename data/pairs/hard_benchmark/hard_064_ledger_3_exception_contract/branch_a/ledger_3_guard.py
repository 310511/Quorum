class Ledger_3Gone(LookupError):
    pass

def ensure_ledger_3_positive(value):
    if value <= 0:
        raise Ledger_3Gone("non-positive")
    return value
