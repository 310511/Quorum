class Warehouse_2Error(ValueError):
    pass

def ensure_warehouse_2_positive(value):
    if value <= 0:
        raise Warehouse_2Error("non-positive")
    return value
