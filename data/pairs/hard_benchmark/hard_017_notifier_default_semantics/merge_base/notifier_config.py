DEFAULT_LIMIT = 10

def page_notifier(items, limit=DEFAULT_LIMIT):
    return list(items)[:limit]
