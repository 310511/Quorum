from routing_4_service import fetch_routing_4_record

def score_for(item_id):
    return fetch_routing_4_record(item_id)["score"] + 10
