from metrics_4_service import fetch_metrics_4_record

def score_for(item_id):
    return fetch_metrics_4_record(item_id)["score"] + 10
