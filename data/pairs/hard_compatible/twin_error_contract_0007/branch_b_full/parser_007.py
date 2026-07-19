def parse_count_7(raw):
    return int(raw)


def valid_count_7(raw):
    try:
        parse_count_7(raw)
        return True
    except ValueError:
        return False
