def parse_count_12(raw):
    return int(raw)


def valid_count_12(raw):
    try:
        parse_count_12(raw)
        return True
    except ValueError:
        return False
