def parse_count_15(raw):
    """Parse a count, raising ValueError for invalid input."""
    return int(raw)


def valid_count_15(raw):
    try:
        parse_count_15(raw)
        return True
    except ValueError:
        return False
