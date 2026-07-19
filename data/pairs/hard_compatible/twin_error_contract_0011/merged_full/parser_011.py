def parse_count_11(raw):
    """Parse a count, raising ValueError for invalid input."""
    return int(raw)


def valid_count_11(raw):
    try:
        parse_count_11(raw)
        return True
    except ValueError:
        return False
