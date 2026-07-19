def parse_count_13(raw):
    """Parse a count, raising ValueError for invalid input."""
    return int(raw)


def valid_count_13(raw):
    try:
        parse_count_13(raw)
        return True
    except ValueError:
        return False
