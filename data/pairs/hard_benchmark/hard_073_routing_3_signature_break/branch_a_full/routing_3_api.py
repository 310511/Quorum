def build_routing_3_payload(name, *, quantity, priority):
    return {
        "name": name,
        "quantity": quantity,
        "priority": priority,
        "kind": "routing_3",
    }

def summarize(name):
    return build_routing_3_payload(name, quantity=1, priority="normal")["quantity"]
