from inventory_utils import normalize_inventory_token

def pipeline_key(value):
    return "key:" + normalize_inventory_token(value)
