def build_pricing_2_payload(name, *, quantity, priority):
    return {
        "name": name,
        "quantity": quantity,
        "priority": priority,
        "kind": "pricing_2",
    }

def summarize(name):
    return build_pricing_2_payload(name, quantity=1, priority="normal")["quantity"]
