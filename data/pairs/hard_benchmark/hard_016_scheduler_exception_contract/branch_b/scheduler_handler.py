from scheduler_guard import ensure_scheduler_positive, SchedulerError

def safe_scheduler(value):
    try:
        return ensure_scheduler_positive(value)
    except SchedulerError:
        return 0
