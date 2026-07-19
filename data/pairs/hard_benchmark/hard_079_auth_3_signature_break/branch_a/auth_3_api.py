def build_auth_3_payload(name, *, quantity, priority):
    return {
        "name": name,
        "quantity": quantity,
        "priority": priority,
        "kind": "auth_3",
    }

def summarize(name):
    return build_auth_3_payload(name, quantity=1, priority="normal")["quantity"]
