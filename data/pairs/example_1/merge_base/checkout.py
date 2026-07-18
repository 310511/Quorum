def finalize_order(cart):
    """Apply tax and return final amount."""
    subtotal = sum(item["price"] for item in cart)
    tax = subtotal * 0.08
    return subtotal + tax
