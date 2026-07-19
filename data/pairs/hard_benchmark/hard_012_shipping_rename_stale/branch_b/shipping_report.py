from shipping_core import compute_shipping_total

def report_line(items):
    return compute_shipping_total(items) * 2
