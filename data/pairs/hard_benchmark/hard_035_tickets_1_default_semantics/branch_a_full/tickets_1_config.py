DEFAULT_LIMIT = 3

def page_tickets_1(items, limit=DEFAULT_LIMIT):
    return list(items)[:limit]
