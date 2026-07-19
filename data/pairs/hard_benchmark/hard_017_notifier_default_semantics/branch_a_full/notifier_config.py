DEFAULT_LIMIT = 3

def page_notifier(items, limit=DEFAULT_LIMIT):
    return list(items)[:limit]
