from parser_4_guard import ensure_parser_4_positive, Parser_4Error

def safe_parser_4(value):
    try:
        return ensure_parser_4_positive(value)
    except Parser_4Error:
        return 0
