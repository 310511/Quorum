from scheduler_3_guard import ensure_scheduler_3_positive, Scheduler_3Error

def safe_scheduler_3(value):
    try:
        return ensure_scheduler_3_positive(value)
    except Scheduler_3Error:
        return 0
