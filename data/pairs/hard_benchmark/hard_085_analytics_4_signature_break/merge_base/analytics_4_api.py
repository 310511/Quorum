def build_analytics_4_payload(name, quantity=1):
    return {"name": name, "quantity": quantity, "kind": "analytics_4"}

def summarize(name):
    return build_analytics_4_payload(name)["quantity"]
