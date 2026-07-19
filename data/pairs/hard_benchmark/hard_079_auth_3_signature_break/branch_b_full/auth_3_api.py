def build_auth_3_payload(name, quantity=1):
    return {"name": name, "quantity": quantity, "kind": "auth_3"}

def summarize(name):
    return build_auth_3_payload(name)["quantity"]
