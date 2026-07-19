from routing_api import build_routing_payload

def client_order(name):
    # Relies on old positional/default signature.
    return build_routing_payload(name, 5)
