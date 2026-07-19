from analytics_config import page_analytics

def preview_analytics():
    # Depends on historical default of 10.
    return page_analytics(range(20))
