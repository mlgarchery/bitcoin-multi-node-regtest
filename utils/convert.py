
def find_type_and_convert(s: str):
    """
    Convert the string to a int or a boolean
    when possible.
    """
    if s=="false":
        return False
    if s=="true":
        return True
    try:
        return int(s)
    except:
        return s