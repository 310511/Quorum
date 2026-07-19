from inventory_4_guard import ensure_inventory_4_positive, Inventory_4Error

def safe_inventory_4(value):
    try:
        return ensure_inventory_4_positive(value)
    except Inventory_4Error:
        return 0
