def parse_count_8(raw):
    """Parse a count, raising ValueError for invalid input."""
    return int(raw)


def valid_count_8(raw):
    try:
        parse_count_8(raw)
        return True
    except ValueError:
        return False
