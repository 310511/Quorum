from pricing_3_service import fetch_pricing_3_record

def score_for(item_id):
    return fetch_pricing_3_record(item_id)["score"] + 10
