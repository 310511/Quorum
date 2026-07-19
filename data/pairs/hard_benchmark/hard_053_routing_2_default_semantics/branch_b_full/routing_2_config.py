DEFAULT_LIMIT = 10

def page_routing_2(items, limit=DEFAULT_LIMIT):
    return list(items)[:limit]
