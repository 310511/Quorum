from routing_3_api import build_routing_3_payload

def client_order(name):
    # Relies on old positional/default signature.
    return build_routing_3_payload(name, 5)
