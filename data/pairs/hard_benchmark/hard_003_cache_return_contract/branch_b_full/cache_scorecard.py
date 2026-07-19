from cache_service import fetch_cache_record

def score_for(item_id):
    return fetch_cache_record(item_id)["score"] + 10
