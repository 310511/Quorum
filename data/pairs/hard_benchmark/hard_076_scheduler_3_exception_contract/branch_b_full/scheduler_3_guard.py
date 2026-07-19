class Scheduler_3Error(ValueError):
    pass

def ensure_scheduler_3_positive(value):
    if value <= 0:
        raise Scheduler_3Error("non-positive")
    return value
