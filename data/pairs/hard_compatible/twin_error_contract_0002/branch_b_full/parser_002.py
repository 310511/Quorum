def parse_count_2(raw):
    return int(raw)


def valid_count_2(raw):
    try:
        parse_count_2(raw)
        return True
    except ValueError:
        return False
