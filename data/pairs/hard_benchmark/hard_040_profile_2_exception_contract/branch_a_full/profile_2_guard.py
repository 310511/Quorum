class Profile_2Gone(LookupError):
    pass

def ensure_profile_2_positive(value):
    if value <= 0:
        raise Profile_2Gone("non-positive")
    return value
