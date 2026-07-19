from pricing_2_api import build_pricing_2_payload

def client_order(name):
    # Relies on old positional/default signature.
    return build_pricing_2_payload(name, 5)
