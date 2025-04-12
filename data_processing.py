import psycopg2
from dotenv import load_dotenv
import os
import datetime
from stravalib.client import Client
import json
import pandas as pd

load_dotenv()

client = Client()

def save_activities_to_db():
    with open('tokens.json', 'r') as file:
        tokens = json.load(file)
    client.access_token = tokens["access_token"]

    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )
    cursor = conn.cursor()

    athlete = client.get_athlete()
    atividades = client.get_activities(before=datetime.datetime.now(), limit=6)
    for atividade in atividades:
        if atividade.type.root == 'WeightTraining':
            continue
        
        cursor.execute("SELECT 1 FROM atividades WHERE activity_id = %s", (atividade.id,))
        if cursor.fetchone() is not None: # Verifica se a atividade já existe
            continue
        
        atv_datetime = {'date': str(pd.to_datetime(atividade.start_date_local).date().strftime('%d-%m-%Y')),
                        'time': str(pd.to_datetime(atividade.start_date_local).time())}
        
        cursor.execute('''INSERT INTO atividades (athlete_name, activity_id, activitie_name, elapsed_time, sport_type, started_date, started_time, distance)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id''',
                    (f'{athlete.firstname} {athlete.lastname}',
                     atividade.id,
                     atividade.name,
                     atividade.elapsed_time,
                     atividade.type.root,
                     atv_datetime['date'],
                     atv_datetime['time'],
                     round(atividade.distance / 1000, 2)))
        activitie_id = cursor.fetchone()[0]
        conn.commit()

        atv_stream = client.get_activity_streams(activity_id=atividade.id,
                                        types=["latlng", "altitude", "heartrate", "velocity_smooth", "grade_smooth"],
                                        resolution="low",
                                        series_type="time")
        latlng = atv_stream['latlng'].data   
        altitude = atv_stream['altitude'].data
        heartrate = atv_stream['heartrate'].data 
        velocity = atv_stream['velocity_smooth'].data
        smooth_grade = atv_stream['grade_smooth'].data
        heart_zones = process_heartzone(heartrate, atividade)

        rows = [
            (activitie_id, lat, lon, alt, hr, round(vel * 3.6, 2), grade, hr_zone)
            for (lat, lon), alt, hr, vel, grade, hr_zone in zip(latlng, altitude, heartrate, velocity, smooth_grade, heart_zones)
        ]

        cursor.executemany('''INSERT INTO detalhes (activitie_id, lat, long, altitude, heartrate, speed, smooth_grade, heart_zones)
                              VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''', rows)
        conn.commit()
        atv_datetime.clear()
    cursor.close()
    conn.close()
    
def process_heartzone(heartrate, atividade):
    defined_zones = {}
    zones = []
    for idx, zone in enumerate(atividade.zones[0].distribution_buckets):
        defined_zones[idx+1] = [zone.min, zone.max]
    for bpm in heartrate:
        if bpm <= defined_zones[1][1]:
            zones.append(1)
        elif bpm <= defined_zones[2][1]:
            zones.append(2)
        elif bpm <= defined_zones[3][1]:
            zones.append(3)
        elif bpm <= defined_zones[4][1]:
            zones.append(4)
        else:
            zones.append(5)
    return zones

# TODO:
    ''''
    1. Salvar atividade.id para verificar se já existe na tabela atividades (não adicionar se já existe)
    2. Adicionar dados das zonas de FC em detalhes - OK
    3. Adicionar zonas de fc em atividades
    '''