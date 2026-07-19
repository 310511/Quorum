def fetch_tickets_3_record(item_id):
    # New contract: nested payload, no top-level score.
    return {"id": item_id, "status": "ok", "meta": {"score": 1}}

def status_of(item_id):
    return fetch_tickets_3_record(item_id)["status"]
