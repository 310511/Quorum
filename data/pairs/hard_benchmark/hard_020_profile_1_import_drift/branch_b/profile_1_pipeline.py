from profile_1_utils import normalize_profile_1_token

def pipeline_key(value):
    return "key:" + normalize_profile_1_token(value)
