def build_metrics_3_payload(name, quantity=1):
    return {"name": name, "quantity": quantity, "kind": "metrics_3"}

def summarize(name):
    return build_metrics_3_payload(name)["quantity"]
