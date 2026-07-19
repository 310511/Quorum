from profile_2_guard import ensure_profile_2_positive, Profile_2Error

def safe_profile_2(value):
    try:
        return ensure_profile_2_positive(value)
    except Profile_2Error:
        return 0
