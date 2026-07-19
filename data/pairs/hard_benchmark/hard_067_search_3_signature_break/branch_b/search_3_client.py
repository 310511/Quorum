from search_3_api import build_search_3_payload

def client_order(name):
    # Relies on old positional/default signature.
    return build_search_3_payload(name, 5)
