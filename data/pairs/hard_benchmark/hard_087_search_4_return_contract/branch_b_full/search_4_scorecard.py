from search_4_service import fetch_search_4_record

def score_for(item_id):
    return fetch_search_4_record(item_id)["score"] + 10
