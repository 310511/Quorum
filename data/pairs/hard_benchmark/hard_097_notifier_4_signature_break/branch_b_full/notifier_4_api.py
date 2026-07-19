def build_notifier_4_payload(name, quantity=1):
    return {"name": name, "quantity": quantity, "kind": "notifier_4"}

def summarize(name):
    return build_notifier_4_payload(name)["quantity"]
