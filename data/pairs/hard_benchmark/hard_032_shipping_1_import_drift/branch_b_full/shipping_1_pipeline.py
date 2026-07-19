from shipping_1_utils import normalize_shipping_1_token

def pipeline_key(value):
    return "key:" + normalize_shipping_1_token(value)
