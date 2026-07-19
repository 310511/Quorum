def build_catalog_4_payload(name, quantity=1):
    return {"name": name, "quantity": quantity, "kind": "catalog_4"}

def summarize(name):
    return build_catalog_4_payload(name)["quantity"]
