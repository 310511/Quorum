from ledger_2_utils import normalize_ledger_2_token

def pipeline_key(value):
    return "key:" + normalize_ledger_2_token(value)
