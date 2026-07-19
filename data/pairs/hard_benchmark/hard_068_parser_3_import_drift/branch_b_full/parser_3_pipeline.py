from parser_3_utils import normalize_parser_3_token

def pipeline_key(value):
    return "key:" + normalize_parser_3_token(value)
