def parse_count_14(raw):
    return int(raw)


def valid_count_14(raw):
    try:
        parse_count_14(raw)
        return True
    except ValueError:
        return False
