from notifier_config import page_notifier

def preview_notifier():
    # Depends on historical default of 10.
    return page_notifier(range(20))
