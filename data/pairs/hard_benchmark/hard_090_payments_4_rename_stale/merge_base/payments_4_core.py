def compute_payments_4_total(items):
    return sum(int(x) for x in items)

def format_total(items):
    return "total=" + str(compute_payments_4_total(items))
