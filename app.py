import os
import psycopg2
from flask import Flask, request, render_template, redirect

app = Flask(__name__)

# Hole PostgreSQL-Verbindungs-URL aus Umgebungsvariablen
DATABASE_URL = os.environ.get("DATABASE_URL")

# Initialisiere Datenbankverbindung
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return conn

# Tabelle erstellen (nur beim ersten Start erforderlich)
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS availability (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            weekday TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.route('/', methods=['GET'])
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT name, role, weekday, start_time, end_time FROM availability ORDER BY weekday, start_time")
    entries = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', entries=entries)

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    role = request.form['role']
    weekday = request.form['weekday']
    start_time = request.form['start_time']
    end_time = request.form['end_time']

    conn = get_db_connection()
    cur = conn.cursor()

    # Prüfen, ob Spieler bereits einen Eintrag hat
    cur.execute("SELECT id FROM availability WHERE name = %s", (name,))
    existing = cur.fetchone()

    if existing:
        cur.execute("""
            UPDATE availability
            SET role = %s, weekday = %s, start_time = %s, end_time = %s
            WHERE name = %s
        """, (role, weekday, start_time, end_time, name))
    else:
        cur.execute("""
            INSERT INTO availability (name, role, weekday, start_time, end_time)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, role, weekday, start_time, end_time))

    conn.commit()
    cur.close()
    conn.close()

    return redirect('/')

if __name__ == '__main__':
    init_db()  # nur beim lokalen Start, nicht bei Render nötig
    app.run(debug=True)
