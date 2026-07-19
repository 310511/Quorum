def build_search_payload(name, quantity=1):
    return {"name": name, "quantity": quantity, "kind": "search"}

def summarize(name):
    return build_search_payload(name)["quantity"]
