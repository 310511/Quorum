from search_api import build_search_payload

def client_order(name):
    # Relies on old positional/default signature.
    return build_search_payload(name, 5)
