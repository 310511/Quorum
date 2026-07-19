DEFAULT_LIMIT = 10

def page_catalog(items, limit=DEFAULT_LIMIT):
    return list(items)[:limit]
