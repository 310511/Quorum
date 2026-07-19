def build_metrics_payload(name, quantity=1):
    return {"name": name, "quantity": quantity, "kind": "metrics"}

def summarize(name):
    return build_metrics_payload(name)["quantity"]
