class Parser_1Gone(LookupError):
    pass

def ensure_parser_1_positive(value):
    if value <= 0:
        raise Parser_1Gone("non-positive")
    return value
