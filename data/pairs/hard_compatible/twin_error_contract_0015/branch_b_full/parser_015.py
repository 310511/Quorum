def parse_count_15(raw):
    return int(raw)


def valid_count_15(raw):
    try:
        parse_count_15(raw)
        return True
    except ValueError:
        return False
