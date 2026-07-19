from analytics_1_api import build_analytics_1_payload

def client_order(name):
    # Relies on old positional/default signature.
    return build_analytics_1_payload(name, 5)
