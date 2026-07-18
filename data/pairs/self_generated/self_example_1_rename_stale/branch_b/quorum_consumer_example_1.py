"""Independent caller added by Branch B."""

from calculator import add


def call_original(*args, **kwargs):
    return add(*args, **kwargs)
