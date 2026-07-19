def build_catalog_4_payload(name, *, quantity, priority):
    return {
        "name": name,
        "quantity": quantity,
        "priority": priority,
        "kind": "catalog_4",
    }

def summarize(name):
    return build_catalog_4_payload(name, quantity=1, priority="normal")["quantity"]
