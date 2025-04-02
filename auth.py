from stravalib.client import Client
from stravalib import unit_helper
from flask import Flask, request, redirect, jsonify
from dotenv import load_dotenv, dotenv_values
import json
import matplotlib.pyplot as plt
import pandas as pd


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
        
        
    #--------------------------
    
    with open('tokens.json', 'r') as file:
        tokens = json.load(file)
    
    load_dotenv()
    if client.protocol._token_expired(): # caso token expirado
        new_token = client.refresh_access_token(
            client_id=dotenv_values()["CLIENT_ID"],
            client_secret=dotenv_values()["CLIENT_SECRET"],
            refresh_token=tokens["refresh_token"],
        )
        
        tokens["access_token"] = new_token["access_token"]
        tokens["refresh_token"] = new_token["refresh_token"]
        tokens["expires_at"] = new_token["expires_at"]

        with open('tokens.json', 'w') as file: # atualiza tokens json
            json.dump(tokens, file)


    athlete = client.get_athlete()
    print(f"Hi, {athlete.firstname} Welcome to stravalib!")

    atividades = client.get_activities(before="2025-04-02", limit=2)
    df_atividade = pd.DataFrame(columns=['id', 'name', 'start_date', 'distance', 'moving_time', 'elapsed_time', 'average_speed', 'average_heartrate'])
    df_detalhes = pd.DataFrame(columns=['id', 'lat', 'long', 'altitude', 'heartrate', 'velocity_smooth'])

    # últimas atividades
    dados_expandidos1 = []
    dados_expandidos2 = []
    for atividade in atividades:
        df_tmp1 = pd.DataFrame({
            'id': [atividade.id],
            'name': [atividade.name],
            'start_date': [atividade.start_date.isoformat()],
            'distance': [float(atividade.distance)],
            'moving_time': [atividade.moving_time],
            'elapsed_time': [atividade.elapsed_time],
            'average_speed': [float(atividade.average_speed)],
            'average_heartrate': [atividade.average_heartrate]
        })
        
        atv_stream = client.get_activity_streams(activity_id=atividade.id,
                                        types=["latlng", "altitude", "heartrate", "velocity_smooth"],
                                        resolution="low",
                                        series_type="time")
        df_tmp2 = pd.DataFrame({
            'id': [atividade.id] * len(atv_stream['latlng'].data),  # Repetir o ID para todas as linhas
            'lat': [point[0] for point in atv_stream['latlng'].data],
            'long': [point[1] for point in atv_stream['latlng'].data],
            'altitude': atv_stream['altitude'].data,
            'heartrate': atv_stream['heartrate'].data,
            'velocity_smooth': atv_stream['velocity_smooth'].data
        })

        dados_expandidos1.append(df_tmp1)
        dados_expandidos2.append(df_tmp2)

    # Concatenar todos os dados verticalmente
    df_atividade = pd.concat(dados_expandidos1, ignore_index=True)
    df_detalhes = pd.concat(dados_expandidos2, ignore_index=True)
        
    print(df_atividade.info())
    print(df_detalhes.info())
    
    dados_json = {
        'atividades': df_atividade.to_dict(orient="records"),
        'detalhes': df_detalhes.to_dict(orient="records")
    }
    

    return jsonify(dados_json)
    
    # return f'Tokens de acesso obtidos e salvos com sucesso!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
