from shipping_4_utils import normalize_shipping_4_token

def pipeline_key(value):
    return "key:" + normalize_shipping_4_token(value)
