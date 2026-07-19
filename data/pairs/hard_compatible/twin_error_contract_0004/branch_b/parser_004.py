def parse_count_4(raw):
    return int(raw)


def valid_count_4(raw):
    try:
        parse_count_4(raw)
        return True
    except ValueError:
        return False
