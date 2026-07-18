from utils import calculate_total

def finalize_order(cart):
    """Apply tax and return final amount."""
    subtotal = calculate_total(cart)
    tax = subtotal * 0.08
    return subtotal + tax
