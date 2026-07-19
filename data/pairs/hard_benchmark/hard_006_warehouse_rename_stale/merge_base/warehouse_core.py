def compute_warehouse_total(items):
    return sum(int(x) for x in items)

def format_total(items):
    return "total=" + str(compute_warehouse_total(items))
