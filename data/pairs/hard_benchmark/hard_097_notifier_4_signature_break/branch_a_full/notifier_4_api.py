def build_notifier_4_payload(name, *, quantity, priority):
    return {
        "name": name,
        "quantity": quantity,
        "priority": priority,
        "kind": "notifier_4",
    }

def summarize(name):
    return build_notifier_4_payload(name, quantity=1, priority="normal")["quantity"]
