def build_analytics_1_payload(name, quantity=1):
    return {"name": name, "quantity": quantity, "kind": "analytics_1"}

def summarize(name):
    return build_analytics_1_payload(name)["quantity"]
