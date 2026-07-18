"""Independent caller added by Branch B."""

from scoring_0003 import compute_total


def call_original(*args, **kwargs):
    return compute_total(*args, **kwargs)
