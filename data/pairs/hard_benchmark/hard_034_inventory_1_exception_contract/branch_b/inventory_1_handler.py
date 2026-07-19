from inventory_1_guard import ensure_inventory_1_positive, Inventory_1Error

def safe_inventory_1(value):
    try:
        return ensure_inventory_1_positive(value)
    except Inventory_1Error:
        return 0
