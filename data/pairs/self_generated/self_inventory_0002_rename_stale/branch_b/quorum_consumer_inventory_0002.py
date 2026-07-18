"""Independent caller added by Branch B."""

from inventory_0002 import compute_available


def call_original(*args, **kwargs):
    return compute_available(*args, **kwargs)
