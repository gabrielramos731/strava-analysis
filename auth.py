from stravalib.client import Client
from dotenv import load_dotenv, dotenv_values
import json
import os

load_dotenv()

CLIENT_ID =  os.environ.get("CLIENT_ID")
CLIENT_SECRET =  os.environ.get("CLIENT_SECRET")

client = Client()

def get_authorization_url(redirect_uri):
    return client.authorization_url(client_id=CLIENT_ID, redirect_uri=redirect_uri)

def exchange_code_for_token(code):
    token_response = client.exchange_code_for_token(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        code=code,
    )
    tokens = {
        "access_token": token_response["access_token"],
        "refresh_token": token_response["refresh_token"],
        "expires_at": token_response["expires_at"],
    }
    with open("tokens.json", "w") as token_file:
        json.dump(tokens, token_file)
    return tokens

def refresh_access_token():
    with open("tokens.json", "r") as file:
        tokens = json.load(file)
    new_token = client.refresh_access_token(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        refresh_token=tokens["refresh_token"],
    )
    tokens.update(new_token)
    with open("tokens.json", "w") as file:
        json.dump(tokens, file)
    return tokens
