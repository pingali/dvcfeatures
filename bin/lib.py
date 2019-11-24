# Multilevel dictionary merge. 
def merge(a, b, path=None):
    "merges b into a"
    if path is None:
        path = []
    for key in b:
        if ((key in a) and 
            (isinstance(a[key], dict) and isinstance(b[key], dict))):
            merge(a[key], b[key], path + [str(key)])
        else:
            a[key] = b[key]

    return a

