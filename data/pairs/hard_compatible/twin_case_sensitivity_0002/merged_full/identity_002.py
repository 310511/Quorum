def same_code_2(left, right):
    """Return True if left equals right exactly (case-sensitive)."""
    return left == right


def authorized_2(presented, required):
    return same_code_2(presented, required)
