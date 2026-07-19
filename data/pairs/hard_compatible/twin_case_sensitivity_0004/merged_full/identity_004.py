def same_code_4(left, right):
    """Return True if left equals right exactly (case-sensitive)."""
    return left == right


def authorized_4(presented, required):
    return same_code_4(presented, required)
