class Inventory_1Gone(LookupError):
    pass

def ensure_inventory_1_positive(value):
    if value <= 0:
        raise Inventory_1Gone("non-positive")
    return value
