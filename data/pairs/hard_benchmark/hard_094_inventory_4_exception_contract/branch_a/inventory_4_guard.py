class Inventory_4Gone(LookupError):
    pass

def ensure_inventory_4_positive(value):
    if value <= 0:
        raise Inventory_4Gone("non-positive")
    return value
