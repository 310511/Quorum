def parse_count_16(raw):
    return int(raw)


def valid_count_16(raw):
    try:
        parse_count_16(raw)
        return True
    except ValueError:
        return False
