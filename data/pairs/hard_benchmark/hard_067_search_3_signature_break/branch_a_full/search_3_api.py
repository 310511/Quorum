def build_search_3_payload(name, *, quantity, priority):
    return {
        "name": name,
        "quantity": quantity,
        "priority": priority,
        "kind": "search_3",
    }

def summarize(name):
    return build_search_3_payload(name, quantity=1, priority="normal")["quantity"]
