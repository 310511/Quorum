"""Independent caller added by Branch B."""

from shipping_0004 import compute_cost


def call_original(*args, **kwargs):
    return compute_cost(*args, **kwargs)
