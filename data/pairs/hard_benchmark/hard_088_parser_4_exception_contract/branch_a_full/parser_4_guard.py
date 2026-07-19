class Parser_4Gone(LookupError):
    pass

def ensure_parser_4_positive(value):
    if value <= 0:
        raise Parser_4Gone("non-positive")
    return value
