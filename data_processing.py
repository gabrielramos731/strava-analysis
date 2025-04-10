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
    atividades = client.get_activities(before=datetime.datetime.now(), limit=5)

    for atividade in atividades:
        if atividade.type.root == 'WeightTraining':
            continue
        
        atv_datetime = {'date': str(pd.to_datetime(atividade.start_date_local).date().strftime('%d-%m-%Y')),
                        'time': str(pd.to_datetime(atividade.start_date_local).time())}
        
        cursor.execute('''INSERT INTO atividades (athlete_name, activitie_name, elapsed_time, sport_type, started_date, started_time, distance)
                    VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id''',
                    (f'{athlete.firstname} {athlete.lastname}',
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

        rows = [
            (activitie_id, lat, lon, alt, hr, round(vel * 3.6, 2), grade)
            for (lat, lon), alt, hr, vel, grade in zip(latlng, altitude, heartrate, velocity, smooth_grade)
        ]

        cursor.executemany('''INSERT INTO detalhes (activitie_id, lat, long, altitude, heartrate, speed, smooth_grade)
                              VALUES (%s, %s, %s, %s, %s, %s, %s)''', rows)
        conn.commit()
        atv_datetime.clear()
    cursor.close()
    conn.close()