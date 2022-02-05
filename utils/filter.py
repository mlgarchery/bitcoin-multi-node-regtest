
from curses import KEY_UNDO
from typing import List


def filter_dict(obj: dict, keys: List[str], l: list):
    """
    Add to l the dicts of obj containing key
    """
    # termination
    if not isinstance(obj, dict): return
    if all(map(lambda x: x in obj, keys)):
        l.append({key: obj[key] for key in keys})
    # recursivity
    for v in obj.values():
        filter_dict(v, keys, l)
        if isinstance(v, list):
            for el in v:
                filter_dict(el, keys, l)

if __name__ == "__main__":
    l = []
    obj = {
        "hey": {
            "hey": "salut",
            "salut": {"hey": "yo"}
        },
        "hello": [
            {"hey": "in list"},
            {"allo": "?", "hey": "allo"},
            {}
        ],
        "list": ["of", "string"]
    }

    filter_dict(obj, ["hey", "allo"], l)
    for el in l:
        print(el)
