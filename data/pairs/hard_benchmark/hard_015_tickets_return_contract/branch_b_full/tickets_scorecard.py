from tickets_service import fetch_tickets_record

def score_for(item_id):
    return fetch_tickets_record(item_id)["score"] + 10
