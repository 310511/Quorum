def same_code_9(left, right):
    """Return True if left equals right exactly (case-sensitive)."""
    return left == right


def authorized_9(presented, required):
    return same_code_9(presented, required)
