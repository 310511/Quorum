def parse_count_9(raw):
    """Parse a count, raising ValueError for invalid input."""
    return int(raw)


def valid_count_9(raw):
    try:
        parse_count_9(raw)
        return True
    except ValueError:
        return False
