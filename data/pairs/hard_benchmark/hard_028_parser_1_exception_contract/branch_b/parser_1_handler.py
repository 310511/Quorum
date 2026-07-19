from parser_1_guard import ensure_parser_1_positive, Parser_1Error

def safe_parser_1(value):
    try:
        return ensure_parser_1_positive(value)
    except Parser_1Error:
        return 0
