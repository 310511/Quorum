def build_pricing_2_payload(name, quantity=1):
    return {"name": name, "quantity": quantity, "kind": "pricing_2"}

def summarize(name):
    return build_pricing_2_payload(name)["quantity"]
