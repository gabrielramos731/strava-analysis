import sqlite3

def initialize_database():
    conn = sqlite3.connect('strava_data.db')
    cursor = conn.cursor()
    
    cursor.execute('DROP TABLE IF EXISTS atividades')
    cursor.execute('DROP TABLE IF EXISTS detalhes')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS atividades(
                    id INTEGER PRIMARY KEY,
                    athlete_name TEXT,
                    activitie_name TEXT,
                    elapsed_time TEXT,
                    started_date TEXT,
                    started_time TEXT,
                    sport_type TEXT,
                    distance REAL
                    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS detalhes(
                        activitie_id INTEGER,
                        lat REAL,
                        long REAL,
                        altitude REAL,
                        heartrate INTEGER,
                        speed REAL,
                        smooth_grade REAL,
                        FOREIGN KEY(activitie_id) REFERENCES atividades(id)
                        )''')
    conn.commit()
    conn.close()