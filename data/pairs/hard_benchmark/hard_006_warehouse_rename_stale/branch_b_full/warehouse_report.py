from warehouse_core import compute_warehouse_total

def report_line(items):
    return compute_warehouse_total(items) * 2
