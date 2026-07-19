def parse_count_17(raw):
    return int(raw)


def valid_count_17(raw):
    try:
        parse_count_17(raw)
        return True
    except ValueError:
        return False
