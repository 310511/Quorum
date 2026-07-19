from catalog_2_service import fetch_catalog_2_record

def score_for(item_id):
    return fetch_catalog_2_record(item_id)["score"] + 10
