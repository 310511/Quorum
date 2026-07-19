def same_code_1(left, right):
    """Return True if left equals right exactly (case-sensitive)."""
    return left == right


def authorized_1(presented, required):
    return same_code_1(presented, required)
