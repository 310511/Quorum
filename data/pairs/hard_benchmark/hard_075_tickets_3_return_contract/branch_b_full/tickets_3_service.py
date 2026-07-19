def fetch_tickets_3_record(item_id):
    return {"id": item_id, "status": "ok", "score": 1}

def status_of(item_id):
    return fetch_tickets_3_record(item_id)["status"]
