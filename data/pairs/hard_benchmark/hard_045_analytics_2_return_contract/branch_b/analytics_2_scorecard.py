from analytics_2_service import fetch_analytics_2_record

def score_for(item_id):
    return fetch_analytics_2_record(item_id)["score"] + 10
