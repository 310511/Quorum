def same_code_5(left, right):
    """Return True if left equals right exactly (case-sensitive)."""
    return left == right


def authorized_5(presented, required):
    return same_code_5(presented, required)
