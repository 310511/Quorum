def build_routing_payload(name, quantity=1):
    return {"name": name, "quantity": quantity, "kind": "routing"}

def summarize(name):
    return build_routing_payload(name)["quantity"]
