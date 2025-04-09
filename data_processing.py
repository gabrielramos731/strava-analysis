import sqlite3
import datetime
from stravalib.client import Client
import json

client = Client()

def save_activities_to_db():
    with open('tokens.json', 'r') as file:
        tokens = json.load(file)
    client.access_token = tokens["access_token"]

    conn = sqlite3.connect('strava_data.db')
    cursor = conn.cursor()

    athlete = client.get_athlete()
    atividades = client.get_activities(before=datetime.datetime.now(), limit=10)

    for atividade in atividades:
        if atividade.type.root == 'WeightTraining':
            continue
        
        cursor.execute('''INSERT INTO atividades (id, athlete_name, activitie_name, elapsed_time, sport_type, distance)
                    VALUES (?, ?, ?, ?, ?, ?)''',
                    (atividade.id,
                    f'{athlete.firstname} {athlete.lastname}',
                    atividade.name,
                    atividade.elapsed_time,
                    atividade.type.root,
                    atividade.distance / 1000))
        conn.commit()

        atv_stream = client.get_activity_streams(activity_id=atividade.id,
                                        types=["latlng", "altitude", "heartrate", "velocity_smooth", "grade_smooth"],
                                        resolution="medium",
                                        series_type="time")
        latlng = atv_stream['latlng'].data   
        altitude = atv_stream['altitude'].data
        heartrate = atv_stream['heartrate'].data 
        velocity = atv_stream['velocity_smooth'].data
        smooth_grade = atv_stream['grade_smooth'].data

        rows = [
            (atividade.id, lat, lon, alt, hr, vel * 3.6, grade)
            for (lat, lon), alt, hr, vel, grade in zip(latlng, altitude, heartrate, velocity, smooth_grade)
        ]

        cursor.executemany('''INSERT INTO detalhes VALUES (?, ?, ?, ?, ?, ?, ?)''', rows)
        conn.commit()
    conn.close()