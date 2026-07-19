DEFAULT_LIMIT = 3

def page_cache_1(items, limit=DEFAULT_LIMIT):
    return list(items)[:limit]
