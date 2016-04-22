def median(lst):
    lst = sorted(lst)

    if len(lst) < 1:
        return None

    if len(lst) % 2 == 1:
        return lst[((len(lst)+1)/2)-1]
    else:
        return float(sum(lst[(len(lst)/2)-1:(len(lst)/2)+1]))/2.0


def try_convert(value, value_type, default=None):
    try:
        return value_type(value)
    except:
        return default
