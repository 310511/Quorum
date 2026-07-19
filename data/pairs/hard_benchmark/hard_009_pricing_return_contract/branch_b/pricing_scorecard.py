from pricing_service import fetch_pricing_record

def score_for(item_id):
    return fetch_pricing_record(item_id)["score"] + 10
