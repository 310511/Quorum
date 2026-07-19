def build_notifier_1_payload(name, quantity=1):
    return {"name": name, "quantity": quantity, "kind": "notifier_1"}

def summarize(name):
    return build_notifier_1_payload(name)["quantity"]
