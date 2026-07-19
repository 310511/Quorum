def parse_count_5(raw):
    return int(raw)


def valid_count_5(raw):
    try:
        parse_count_5(raw)
        return True
    except ValueError:
        return False
