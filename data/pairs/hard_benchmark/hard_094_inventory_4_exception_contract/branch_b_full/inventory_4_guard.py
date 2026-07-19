class Inventory_4Error(ValueError):
    pass

def ensure_inventory_4_positive(value):
    if value <= 0:
        raise Inventory_4Error("non-positive")
    return value
