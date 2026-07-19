def parse_count_6(raw):
    """Parse a count, raising ValueError for invalid input."""
    return int(raw)


def valid_count_6(raw):
    try:
        parse_count_6(raw)
        return True
    except ValueError:
        return False
