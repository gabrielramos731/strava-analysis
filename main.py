from stravalib.client import Client
from dotenv import load_dotenv, dotenv_values
import json, time
 
with open('tokens.json', 'r') as file:
    tokens = json.load(file)
    

load_dotenv()
client = Client(
    access_token=tokens["access_token"],
    refresh_token=tokens["refresh_token"],
    token_expires=tokens["expires_at"],
)

if client.protocol._token_expired():
    new_token = client.refresh_access_token(
        client_id=dotenv_values()["CLIENT_ID"],
        client_secret=dotenv_values()["CLIENT_SECRET"],
        refresh_token=tokens["refresh_token"],
    )
    
    tokens["access_token"] = new_token["access_token"]
    tokens["refresh_token"] = new_token["refresh_token"]
    tokens["expires_at"] = new_token["expires_at"]

    with open('tokens.json', 'w') as file:
        json.dump(tokens, file)

athlete = client.get_athlete()
print(f"Hi, {athlete.firstname} Welcome to stravalib!")
