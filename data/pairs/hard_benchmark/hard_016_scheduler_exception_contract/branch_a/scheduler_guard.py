class SchedulerGone(LookupError):
    pass

def ensure_scheduler_positive(value):
    if value <= 0:
        raise SchedulerGone("non-positive")
    return value
