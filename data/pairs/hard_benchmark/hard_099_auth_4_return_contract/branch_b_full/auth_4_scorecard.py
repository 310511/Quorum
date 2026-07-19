from auth_4_service import fetch_auth_4_record

def score_for(item_id):
    return fetch_auth_4_record(item_id)["score"] + 10
