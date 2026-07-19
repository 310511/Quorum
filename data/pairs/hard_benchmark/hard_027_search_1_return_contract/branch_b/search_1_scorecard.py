from search_1_service import fetch_search_1_record

def score_for(item_id):
    return fetch_search_1_record(item_id)["score"] + 10
