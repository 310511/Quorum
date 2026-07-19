from catalog_config import page_catalog

def preview_catalog():
    # Depends on historical default of 10.
    return page_catalog(range(20))
