class Parser_1Error(ValueError):
    pass

def ensure_parser_1_positive(value):
    if value <= 0:
        raise Parser_1Error("non-positive")
    return value
