DEFAULT_LIMIT = 3

def page_catalog(items, limit=DEFAULT_LIMIT):
    return list(items)[:limit]
