def build_auth_payload(name, quantity=1):
    return {"name": name, "quantity": quantity, "kind": "auth"}

def summarize(name):
    return build_auth_payload(name)["quantity"]
