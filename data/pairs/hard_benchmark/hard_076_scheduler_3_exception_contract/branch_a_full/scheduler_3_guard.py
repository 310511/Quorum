class Scheduler_3Gone(LookupError):
    pass

def ensure_scheduler_3_positive(value):
    if value <= 0:
        raise Scheduler_3Gone("non-positive")
    return value
