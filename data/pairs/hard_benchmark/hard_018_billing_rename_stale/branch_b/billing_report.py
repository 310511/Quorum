from billing_core import compute_billing_total

def report_line(items):
    return compute_billing_total(items) * 2
