def same_code_8(left, right):
    """Return True if left equals right exactly (case-sensitive)."""
    return left == right


def authorized_8(presented, required):
    return same_code_8(presented, required)
