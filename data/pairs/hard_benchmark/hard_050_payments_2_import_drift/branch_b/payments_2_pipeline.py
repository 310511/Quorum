from payments_2_utils import normalize_payments_2_token

def pipeline_key(value):
    return "key:" + normalize_payments_2_token(value)
