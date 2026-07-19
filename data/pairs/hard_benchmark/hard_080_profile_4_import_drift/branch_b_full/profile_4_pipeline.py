from profile_4_utils import normalize_profile_4_token

def pipeline_key(value):
    return "key:" + normalize_profile_4_token(value)
