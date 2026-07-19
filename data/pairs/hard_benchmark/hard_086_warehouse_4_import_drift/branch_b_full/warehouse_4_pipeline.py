from warehouse_4_utils import normalize_warehouse_4_token

def pipeline_key(value):
    return "key:" + normalize_warehouse_4_token(value)
