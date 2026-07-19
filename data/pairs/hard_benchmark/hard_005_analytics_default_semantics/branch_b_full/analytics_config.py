DEFAULT_LIMIT = 10

def page_analytics(items, limit=DEFAULT_LIMIT):
    return list(items)[:limit]
