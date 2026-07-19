def same_code_3(left, right):
    """Return True if left equals right exactly (case-sensitive)."""
    return left == right


def authorized_3(presented, required):
    return same_code_3(presented, required)
