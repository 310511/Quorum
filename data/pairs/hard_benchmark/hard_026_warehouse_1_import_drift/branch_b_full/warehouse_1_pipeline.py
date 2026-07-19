from warehouse_1_utils import normalize_warehouse_1_token

def pipeline_key(value):
    return "key:" + normalize_warehouse_1_token(value)
