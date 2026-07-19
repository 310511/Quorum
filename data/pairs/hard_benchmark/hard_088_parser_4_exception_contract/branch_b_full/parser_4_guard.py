class Parser_4Error(ValueError):
    pass

def ensure_parser_4_positive(value):
    if value <= 0:
        raise Parser_4Error("non-positive")
    return value
