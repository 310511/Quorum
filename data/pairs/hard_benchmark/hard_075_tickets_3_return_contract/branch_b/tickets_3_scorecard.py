from tickets_3_service import fetch_tickets_3_record

def score_for(item_id):
    return fetch_tickets_3_record(item_id)["score"] + 10
