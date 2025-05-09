import psycopg2
from dotenv import load_dotenv
import os
import datetime
from stravalib.client import Client
import json
import pandas as pd

load_dotenv()
client = Client()

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )

def get_tokens():
    with open('tokens.json', 'r') as file:
        return json.load(file)

def get_activities(client, limit=3):
    return client.get_activities(before=datetime.datetime.now(), limit=limit)

def insert_zones(cursor, atividade):
    for idx, zone in enumerate(atividade.zones[0].distribution_buckets):
        cursor.execute('''
            INSERT INTO zonas_frequencia (zona_id, minimo, maximo)
            VALUES (%s, %s, %s)
        ''', (idx, int(zone.min), int(zone.max)))

def atividade_ja_existe(cursor, activity_id):
    cursor.execute("SELECT 1 FROM atividades WHERE activity_id = %s", (activity_id,))
    return cursor.fetchone() is not None

def inserir_atividade(cursor, athlete, atividade):
    atv_datetime = {
        'date': pd.to_datetime(atividade.start_date_local).strftime('%d-%m-%Y'),
        'time': pd.to_datetime(atividade.start_date_local).strftime('%H:%M:%S')
    }

    cursor.execute('''
        INSERT INTO atividades (athlete_name, activity_id, activitie_name, elapsed_time, sport_type, started_date, started_time, distance)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
    ''', (
        f'{athlete.firstname} {athlete.lastname}',
        atividade.id,
        atividade.name,
        atividade.elapsed_time,
        atividade.type.root,
        atv_datetime['date'],
        atv_datetime['time'],
        round(atividade.distance / 1000, 2)
    ))
    return cursor.fetchone()[0]

def get_stream_data(client, activity_id):
    return client.get_activity_streams(
        activity_id=activity_id,
        types=["latlng", "time", "distance", "altitude", "heartrate", "velocity_smooth", "grade_smooth"],
        resolution="low",
        series_type="time"
    )

def calcular_zonas_frequencia(atividade, heartrate):
    zones = []
    defined_zones = {idx + 1: [zone.min, zone.max] for idx, zone in enumerate(atividade.zones[0].distribution_buckets)}

    for bpm in heartrate:
        for z_id in range(1, 6):
            if bpm <= defined_zones[z_id][1]:
                zones.append(z_id)
                break
    return zones

def inserir_detalhes(cursor, activitie_id, atividade, atv_stream):
    latlng = atv_stream['latlng'].data
    time = atv_stream['time'].data
    distance = atv_stream['distance'].data
    altitude = atv_stream['altitude'].data
    heartrate = atv_stream['heartrate'].data
    velocity = atv_stream['velocity_smooth'].data
    grade = atv_stream['grade_smooth'].data
    heart_zones = calcular_zonas_frequencia(atividade, heartrate)

    rows = [
        (activitie_id, lat, lon, t, d, alt, hr, round(vel * 3.6, 2), g, hz)
        for (lat, lon), t, d, alt, hr, vel, g, hz
        in zip(latlng, time, distance, altitude, heartrate, velocity, grade, heart_zones)
    ]

    cursor.executemany('''
        INSERT INTO detalhes (activitie_id, lat, long, time, distance, altitude, heartrate, speed, smooth_grade, heart_zones)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', rows)

def save_activities_to_db():
    tokens = get_tokens()
    client.access_token = tokens["access_token"]
    conn = get_db_connection()
    cursor = conn.cursor()

    athlete = client.get_athlete()
    atividades = get_activities(client)

    zonas_criadas = False

    for atividade in atividades:
        if atividade.type.root == 'WeightTraining':
            continue

        if not zonas_criadas:
            insert_zones(cursor, atividade)
            zonas_criadas = True

        if atividade_ja_existe(cursor, atividade.id):
            continue

        activitie_id = inserir_atividade(cursor, athlete, atividade)
        conn.commit()

        atv_stream = get_stream_data(client, atividade.id)
        inserir_detalhes(cursor, activitie_id, atividade, atv_stream)
        conn.commit()

    cursor.close()
    conn.close()
