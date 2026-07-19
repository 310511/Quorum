def build_analytics_1_payload(name, *, quantity, priority):
    return {
        "name": name,
        "quantity": quantity,
        "priority": priority,
        "kind": "analytics_1",
    }

def summarize(name):
    return build_analytics_1_payload(name, quantity=1, priority="normal")["quantity"]
