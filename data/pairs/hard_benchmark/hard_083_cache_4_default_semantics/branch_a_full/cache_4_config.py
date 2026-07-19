DEFAULT_LIMIT = 3

def page_cache_4(items, limit=DEFAULT_LIMIT):
    return list(items)[:limit]
