def parse_count_11(raw):
    return int(raw)


def valid_count_11(raw):
    try:
        parse_count_11(raw)
        return True
    except ValueError:
        return False
