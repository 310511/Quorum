def parse_count_1(raw):
    return int(raw)


def valid_count_1(raw):
    try:
        parse_count_1(raw)
        return True
    except ValueError:
        return False
