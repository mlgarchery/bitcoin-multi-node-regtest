import pprint

def prettyprint(obj, depth=None):
    if isinstance(obj, dict):
        pprint.pprint(obj, indent=2, depth=depth)
    elif isinstance(obj, list):
        for el in obj:
            prettyprint(el, depth=depth)
    elif isinstance(obj, bytes):
        print(obj.decode("utf-8"))
    else:
        print(obj)
