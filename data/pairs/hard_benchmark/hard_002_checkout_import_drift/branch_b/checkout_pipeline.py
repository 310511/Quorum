from checkout_utils import normalize_checkout_token

def pipeline_key(value):
    return "key:" + normalize_checkout_token(value)
