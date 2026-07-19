def build_auth_payload(name, *, quantity, priority):
    return {
        "name": name,
        "quantity": quantity,
        "priority": priority,
        "kind": "auth",
    }

def summarize(name):
    return build_auth_payload(name, quantity=1, priority="normal")["quantity"]
