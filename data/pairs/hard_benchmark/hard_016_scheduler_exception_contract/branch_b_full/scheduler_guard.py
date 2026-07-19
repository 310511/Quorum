class SchedulerError(ValueError):
    pass

def ensure_scheduler_positive(value):
    if value <= 0:
        raise SchedulerError("non-positive")
    return value
