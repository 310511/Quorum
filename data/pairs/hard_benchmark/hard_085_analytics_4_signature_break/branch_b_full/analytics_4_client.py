from analytics_4_api import build_analytics_4_payload

def client_order(name):
    # Relies on old positional/default signature.
    return build_analytics_4_payload(name, 5)
