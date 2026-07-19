def same_code_15(left, right):
    """Return True if left equals right exactly (case-sensitive)."""
    return left == right


def authorized_15(presented, required):
    return same_code_15(presented, required)
