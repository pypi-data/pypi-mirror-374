import base64


def decode(base64_string):
    """
    Decodes a base 64 encoded string.
    """
    try:
        print(base64.b64decode(base64_string.encode('utf-8')).decode('utf-8'))
    except Exception as e:
        print("Decoding error:", e)

def encode(string_value):
    """
    Decodes a base 64 encoded string.
    """
    try:
        print(base64.b64encode(string_value.encode('utf-8')).decode('utf-8'))
    except Exception as e:
        print("Encoding error:", e)        

def run(action=None, str_value=None):
    if action is None or str_value is None:
        print("Usage: b64 <action> <value>")
        return

    if action == "decode":
        decode(str_value)
        return
    
    if action == "encode":
        encode(str_value)
        return
