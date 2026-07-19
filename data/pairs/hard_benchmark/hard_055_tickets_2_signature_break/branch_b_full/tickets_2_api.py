def build_tickets_2_payload(name, quantity=1):
    return {"name": name, "quantity": quantity, "kind": "tickets_2"}

def summarize(name):
    return build_tickets_2_payload(name)["quantity"]
