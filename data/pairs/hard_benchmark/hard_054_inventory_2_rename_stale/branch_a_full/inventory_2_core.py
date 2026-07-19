def compute_inventory_2_total_v2(items):
    return sum(int(x) for x in items)

def format_total(items):
    return "total=" + str(compute_inventory_2_total_v2(items))
