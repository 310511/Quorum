def parse_count_3(raw):
    return int(raw)


def valid_count_3(raw):
    try:
        parse_count_3(raw)
        return True
    except ValueError:
        return False
