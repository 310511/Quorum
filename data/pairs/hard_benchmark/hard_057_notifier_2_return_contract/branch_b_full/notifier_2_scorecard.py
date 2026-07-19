from notifier_2_service import fetch_notifier_2_record

def score_for(item_id):
    return fetch_notifier_2_record(item_id)["score"] + 10
