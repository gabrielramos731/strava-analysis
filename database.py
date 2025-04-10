import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os

load_dotenv()

def initialize_database():
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )
    cursor = conn.cursor()
    
    cursor.execute('DROP TABLE IF EXISTS detalhes')
    cursor.execute('DROP TABLE IF EXISTS atividades')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS atividades(
                    id SERIAL PRIMARY KEY,
                    athlete_name TEXT,
                    activitie_name TEXT,
                    elapsed_time TEXT,
                    started_date TEXT,
                    started_time TEXT,
                    sport_type TEXT,
                    distance REAL
                    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS detalhes(
                        activitie_id INTEGER REFERENCES atividades(id),
                        lat REAL,
                        long REAL,
                        altitude REAL,
                        heartrate INTEGER,
                        speed REAL,
                        smooth_grade REAL
                        )''')
    conn.commit()
    cursor.close()
    conn.close()