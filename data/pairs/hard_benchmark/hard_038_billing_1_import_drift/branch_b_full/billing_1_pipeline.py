from billing_1_utils import normalize_billing_1_token

def pipeline_key(value):
    return "key:" + normalize_billing_1_token(value)
