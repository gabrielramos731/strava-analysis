from stravalib.client import Client
from stravalib import unit_helper
from dotenv import load_dotenv, dotenv_values
import json
import matplotlib.pyplot as plt
import pandas as pd
 
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

    with open('tokens.json', 'w') as file: # atualiza tokens json
        json.dump(tokens, file)


athlete = client.get_athlete()
print(f"Hi, {athlete.firstname} Welcome to stravalib!")

atividades = client.get_activities(before="2025-04-02", limit=2)
df_atividade = pd.DataFrame(columns=['id', 'name', 'start_date', 'distance', 'moving_time', 'elapsed_time', 'average_speed', 'average_heartrate'])
df_detalhes = pd.DataFrame(columns=['id', 'lat', 'long', 'altitude', 'heartrate', 'velocity_smooth'])

# últimas atividades
atv_tmp = {}
detail_tmp = {}
dados_expandidos1 = []
dados_expandidos2 = []
for atividade in atividades:
    df_tmp1 = pd.DataFrame({
        'id': [atividade.id],
        'name': [atividade.name],
        'start_date': [atividade.start_date],
        'distance': [unit_helper.kilometers(atividade.distance)],
        'moving_time': [atividade.moving_time],
        'elapsed_time': [atividade.elapsed_time],
        'average_speed': [unit_helper.kilometers_per_hour(atividade.average_speed)],
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
    
print(df_atividade)
print(df_detalhes)
