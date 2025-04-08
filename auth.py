from stravalib.client import Client
from stravalib import unit_helper
from flask import Flask, request, redirect, jsonify, Response
from dotenv import load_dotenv, dotenv_values
import json
import pandas as pd
import os
import sqlite3


app = Flask(__name__)

CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")

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
        
    save_data()
    return f'Dados atualizados com sucesso! Você já pode fechar essa janela.'
        

    
def save_data():
    
    conn = sqlite3.connect('strava_data.db')
    cursor = conn.cursor()
    
    cursor.execute('DROP TABLE IF EXISTS atividades')
    cursor.execute('DROP TABLE IF EXISTS detalhes')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS atividades(
                    id INTEGER PRIMARY KEY,
                    athlete_name TEXT,
                    activitie_name TEXT,
                    elapsed_time TEXT,
                    sport_type TEXT,
                    distance REAL
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS detalhes(
                        activitie_id INTEGER,
                        lat REAL,
                        long REAL,
                        heartrate INTEGER,
                        speed REAL,
                        FOREIGN KEY(activitie_id) REFERENCES atividades(id)
                        )''')

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
    atividades = client.get_activities(before="2025-04-04", limit=8)

    for atividade in atividades:
        if atividade.type.root == 'WeightTraining':
            continue
        
        # salva resumo da atividade
        cursor.execute('''INSERT INTO atividades (id, athlete_name, activitie_name, elapsed_time, sport_type, distance)
                    VALUES (?, ?, ?, ?, ?, ?)''',
                    (atividade.id,
                    f'{athlete.firstname} {athlete.lastname}',
                    atividade.name,
                    atividade.elapsed_time,
                    atividade.type.root,
                    atividade.distance))
        conn.commit()    
        
        atv_stream = client.get_activity_streams(activity_id=atividade.id,
                                        types=["latlng", "altitude", "heartrate", "velocity_smooth"],
                                        resolution="medium",
                                        series_type="time")
        latlng = atv_stream['latlng'].data    
        heartrate = atv_stream['heartrate'].data 
        velocity = atv_stream['velocity_smooth'].data 

        rows = [
            (atividade.id, lat, lon, hr, vel)
            for (lat, lon), hr, vel in zip(latlng, heartrate, velocity)
        ]
        cursor.executemany('''INSERT INTO detalhes VALUES (?, ?, ?, ?, ?)''', rows)
        conn.commit()
        
    return None

if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=10000) # deploy
    app.run(debug=True) # teste
