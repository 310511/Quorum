from inventory_3_utils import normalize_inventory_3_token

def pipeline_key(value):
    return "key:" + normalize_inventory_3_token(value)
