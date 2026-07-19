from checkout_3_utils import normalize_checkout_3_token

def pipeline_key(value):
    return "key:" + normalize_checkout_3_token(value)
