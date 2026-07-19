from metrics_3_api import build_metrics_3_payload

def client_order(name):
    # Relies on old positional/default signature.
    return build_metrics_3_payload(name, 5)
