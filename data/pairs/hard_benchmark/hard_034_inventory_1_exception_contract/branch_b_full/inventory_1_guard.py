class Inventory_1Error(ValueError):
    pass

def ensure_inventory_1_positive(value):
    if value <= 0:
        raise Inventory_1Error("non-positive")
    return value
