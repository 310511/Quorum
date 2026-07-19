def compute_parser_2_total(items):
    return sum(int(x) for x in items)

def format_total(items):
    return "total=" + str(compute_parser_2_total(items))
