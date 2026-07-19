def build_tickets_2_payload(name, *, quantity, priority):
    return {
        "name": name,
        "quantity": quantity,
        "priority": priority,
        "kind": "tickets_2",
    }

def summarize(name):
    return build_tickets_2_payload(name, quantity=1, priority="normal")["quantity"]
