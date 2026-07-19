from catalog_4_api import build_catalog_4_payload

def client_order(name):
    # Relies on old positional/default signature.
    return build_catalog_4_payload(name, 5)
