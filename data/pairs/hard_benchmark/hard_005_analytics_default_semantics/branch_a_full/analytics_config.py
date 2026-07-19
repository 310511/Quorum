DEFAULT_LIMIT = 3

def page_analytics(items, limit=DEFAULT_LIMIT):
    return list(items)[:limit]
