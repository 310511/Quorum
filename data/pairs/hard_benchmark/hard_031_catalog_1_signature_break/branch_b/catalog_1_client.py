from catalog_1_api import build_catalog_1_payload

def client_order(name):
    # Relies on old positional/default signature.
    return build_catalog_1_payload(name, 5)
