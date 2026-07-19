def same_code_13(left, right):
    """Return True if left equals right exactly (case-sensitive)."""
    return left == right


def authorized_13(presented, required):
    return same_code_13(presented, required)
