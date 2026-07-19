def parse_count_10(raw):
    return int(raw)


def valid_count_10(raw):
    try:
        parse_count_10(raw)
        return True
    except ValueError:
        return False
