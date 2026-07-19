DEFAULT_LIMIT = 10

def page_notifier_3(items, limit=DEFAULT_LIMIT):
    return list(items)[:limit]
