def build_search_3_payload(name, quantity=1):
    return {"name": name, "quantity": quantity, "kind": "search_3"}

def summarize(name):
    return build_search_3_payload(name)["quantity"]
