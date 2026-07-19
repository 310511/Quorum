DEFAULT_LIMIT = 10

def page_tickets_4(items, limit=DEFAULT_LIMIT):
    return list(items)[:limit]
