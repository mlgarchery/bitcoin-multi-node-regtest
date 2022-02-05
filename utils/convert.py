
def str_to_int(s: str):
    """
    Convert the string to int when possible
    """
    try:
        return int(s)
    except:
        return s