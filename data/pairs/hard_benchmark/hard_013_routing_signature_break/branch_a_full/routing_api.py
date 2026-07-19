def build_routing_payload(name, *, quantity, priority):
    return {
        "name": name,
        "quantity": quantity,
        "priority": priority,
        "kind": "routing",
    }

def summarize(name):
    return build_routing_payload(name, quantity=1, priority="normal")["quantity"]
