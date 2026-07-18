# utils.py — shared helpers for order total calculation

def compute_total(items):
    """Sum line-item prices. Used by checkout and reporting."""
    return sum(item["price"] for item in items)
