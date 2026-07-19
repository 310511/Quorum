from auth_3_api import build_auth_3_payload

def client_order(name):
    # Relies on old positional/default signature.
    return build_auth_3_payload(name, 5)
