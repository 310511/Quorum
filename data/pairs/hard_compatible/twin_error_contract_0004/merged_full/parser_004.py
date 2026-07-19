def parse_count_4(raw):
    """Parse a count, raising ValueError for invalid input."""
    return int(raw)


def valid_count_4(raw):
    try:
        parse_count_4(raw)
        return True
    except ValueError:
        return False
