def build_metrics_payload(name, *, quantity, priority):
    return {
        "name": name,
        "quantity": quantity,
        "priority": priority,
        "kind": "metrics",
    }

def summarize(name):
    return build_metrics_payload(name, quantity=1, priority="normal")["quantity"]
