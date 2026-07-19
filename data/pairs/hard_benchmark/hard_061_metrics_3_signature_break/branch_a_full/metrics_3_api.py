def build_metrics_3_payload(name, *, quantity, priority):
    return {
        "name": name,
        "quantity": quantity,
        "priority": priority,
        "kind": "metrics_3",
    }

def summarize(name):
    return build_metrics_3_payload(name, quantity=1, priority="normal")["quantity"]
