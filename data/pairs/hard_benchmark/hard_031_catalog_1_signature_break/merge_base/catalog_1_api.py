def build_catalog_1_payload(name, quantity=1):
    return {"name": name, "quantity": quantity, "kind": "catalog_1"}

def summarize(name):
    return build_catalog_1_payload(name)["quantity"]
