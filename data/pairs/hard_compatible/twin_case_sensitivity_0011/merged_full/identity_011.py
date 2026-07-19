def same_code_11(left, right):
    """Return True if left equals right exactly (case-sensitive)."""
    return left == right


def authorized_11(presented, required):
    return same_code_11(presented, required)
