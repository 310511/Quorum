def build_cache_2_payload(name, quantity=1):
    return {"name": name, "quantity": quantity, "kind": "cache_2"}

def summarize(name):
    return build_cache_2_payload(name)["quantity"]
