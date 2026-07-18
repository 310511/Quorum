"""Independent caller added by Branch B."""

from pricing_0001 import compute_subtotal


def call_original(*args, **kwargs):
    return compute_subtotal(*args, **kwargs)
