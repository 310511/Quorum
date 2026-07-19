def compute_ledger_4_total_v2(items):
    return sum(int(x) for x in items)

def format_total(items):
    return "total=" + str(compute_ledger_4_total_v2(items))
