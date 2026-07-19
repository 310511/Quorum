def compute_billing_3_total(items):
    return sum(int(x) for x in items)

def format_total(items):
    return "total=" + str(compute_billing_3_total(items))
