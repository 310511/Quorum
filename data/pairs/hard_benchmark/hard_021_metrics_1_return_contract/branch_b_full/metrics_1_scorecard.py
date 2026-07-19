from metrics_1_service import fetch_metrics_1_record

def score_for(item_id):
    return fetch_metrics_1_record(item_id)["score"] + 10
