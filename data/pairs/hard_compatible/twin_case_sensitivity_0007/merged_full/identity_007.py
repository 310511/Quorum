def same_code_7(left, right):
    """Return True if left equals right exactly (case-sensitive)."""
    return left == right


def authorized_7(presented, required):
    return same_code_7(presented, required)
