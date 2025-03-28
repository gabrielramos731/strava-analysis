from stravalib.client import Client
import json

CLIENT_ID = 153650
CLIENT_SECRET = "4465c27cac920c33793b42b3700ae047e29e6cd5"

client = Client()
url = client.authorization_url(
    client_id=CLIENT_ID,
    redirect_uri="http://127.0.0.1:5000/authorization",
)

print(url)

token_response = client.exchange_code_for_token(
    client_id=CLIENT_ID, 
    client_secret=CLIENT_SECRET, 
    code="297377fcb803905f78e5572683fced1fde04151f"
)
# The token response above contains both an access_token and a refresh token.
access_token = token_response["access_token"]
refresh_token = token_response["refresh_token"]  # You'll need this in 6 hours
expires_at = token_response["expires_at"]  # When the access token expires

# Save tokens to a JSON file
tokens = {
    "access_token": access_token,
    "refresh_token": refresh_token,
    "expires_at": expires_at,
}

with open("tokens.json", "w") as token_file:
    json.dump(tokens, token_file)

