class Warehouse_2Gone(LookupError):
    pass

def ensure_warehouse_2_positive(value):
    if value <= 0:
        raise Warehouse_2Gone("non-positive")
    return value
