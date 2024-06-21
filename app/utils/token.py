import json
import os
from google.oauth2.credentials import Credentials

def save_credentials(credentials, filepath="credentials.json"):
    with open(filepath, "w") as f:
        json.dump({
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes
        }, f)

def load_credentials(filepath="credentials.json"):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            data = json.load(f)
            return Credentials(**data)
    return None
