from notifier_4_api import build_notifier_4_payload

def client_order(name):
    # Relies on old positional/default signature.
    return build_notifier_4_payload(name, 5)
