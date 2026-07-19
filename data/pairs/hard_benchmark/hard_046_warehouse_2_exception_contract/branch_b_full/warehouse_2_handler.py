from warehouse_2_guard import ensure_warehouse_2_positive, Warehouse_2Error

def safe_warehouse_2(value):
    try:
        return ensure_warehouse_2_positive(value)
    except Warehouse_2Error:
        return 0
