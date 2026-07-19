class Profile_2Error(ValueError):
    pass

def ensure_profile_2_positive(value):
    if value <= 0:
        raise Profile_2Error("non-positive")
    return value
