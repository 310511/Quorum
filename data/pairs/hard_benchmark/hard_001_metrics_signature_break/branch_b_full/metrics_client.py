from metrics_api import build_metrics_payload

def client_order(name):
    # Relies on old positional/default signature.
    return build_metrics_payload(name, 5)
