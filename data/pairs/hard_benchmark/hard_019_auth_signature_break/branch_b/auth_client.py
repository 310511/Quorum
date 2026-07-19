from auth_api import build_auth_payload

def client_order(name):
    # Relies on old positional/default signature.
    return build_auth_payload(name, 5)
