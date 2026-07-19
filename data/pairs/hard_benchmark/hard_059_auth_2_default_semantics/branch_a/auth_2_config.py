DEFAULT_LIMIT = 3

def page_auth_2(items, limit=DEFAULT_LIMIT):
    return list(items)[:limit]
