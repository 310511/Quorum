from scheduler_2_utils import normalize_scheduler_2_token

def pipeline_key(value):
    return "key:" + normalize_scheduler_2_token(value)
