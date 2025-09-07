import base64
import json

def decode(token):
    """
    Decodes a JWT token and prints its header and payload.
    """
    try:
        header_b64, payload_b64, _ = token.split('.')
        header = json.loads(base64.urlsafe_b64decode(header_b64 + '==').decode())
        payload = json.loads(base64.urlsafe_b64decode(payload_b64 + '==').decode())
        print("Header:", header)
        print("Payload:", payload)
    except Exception as e:
        print("Invalid JWT format or decoding error:", e)

def run(action=None, token=None):
    if action is None or token is None:
        print("Usage: jwt <action> <token>")
        return

    if action == "decode":
        decode(token)