def build_notifier_1_payload(name, *, quantity, priority):
    return {
        "name": name,
        "quantity": quantity,
        "priority": priority,
        "kind": "notifier_1",
    }

def summarize(name):
    return build_notifier_1_payload(name, quantity=1, priority="normal")["quantity"]
