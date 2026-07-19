DEFAULT_LIMIT = 10

def page_cache_1(items, limit=DEFAULT_LIMIT):
    return list(items)[:limit]
