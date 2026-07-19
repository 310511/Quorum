from billing_4_utils import normalize_billing_4_token

def pipeline_key(value):
    return "key:" + normalize_billing_4_token(value)
