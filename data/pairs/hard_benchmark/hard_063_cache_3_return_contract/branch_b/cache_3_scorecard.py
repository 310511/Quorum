from cache_3_service import fetch_cache_3_record

def score_for(item_id):
    return fetch_cache_3_record(item_id)["score"] + 10
