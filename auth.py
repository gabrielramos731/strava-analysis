from stravalib.client import Client
import json
from dotenv import dotenv_values
from flask import Flask, request, redirect

app = Flask(__name__)

CLIENT_ID = dotenv_values()["CLIENT_ID"]
CLIENT_SECRET = dotenv_values()["CLIENT_SECRET"]

client = Client()

# Rota inicial: redireciona o usuário para a página de autenticação do Strava
@app.route('/')
def index():
    url = client.authorization_url(
        client_id=CLIENT_ID,
        redirect_uri="http://127.0.0.1:5000/authorization",
    )
    return redirect(url)

# Rota para captura do código de autorização
@app.route('/authorization')
def authorization():
    code = request.args.get('code')
    token_response = client.exchange_code_for_token(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        code=code,
    )

    access_token = token_response["access_token"]
    refresh_token = token_response["refresh_token"]
    expires_at = token_response["expires_at"]

    tokens = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_at": expires_at,
    }

    # Salva os tokens em um arquivo JSON
    with open("tokens.json", "w") as token_file:
        json.dump(tokens, token_file)

    return f'Tokens de acesso obtidos e salvos com sucesso!'

if __name__ == '__main__':
    app.run(debug=True)
