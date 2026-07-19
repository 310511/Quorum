def build_routing_3_payload(name, quantity=1):
    return {"name": name, "quantity": quantity, "kind": "routing_3"}

def summarize(name):
    return build_routing_3_payload(name)["quantity"]
