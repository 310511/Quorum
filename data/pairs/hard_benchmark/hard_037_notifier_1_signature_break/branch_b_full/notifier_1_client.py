from notifier_1_api import build_notifier_1_payload

def client_order(name):
    # Relies on old positional/default signature.
    return build_notifier_1_payload(name, 5)
