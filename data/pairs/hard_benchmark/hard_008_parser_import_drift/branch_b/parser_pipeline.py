from parser_utils import normalize_parser_token

def pipeline_key(value):
    return "key:" + normalize_parser_token(value)
