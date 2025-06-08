from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import time

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS availability (
                    name TEXT,
                    role TEXT,
                    weekday TEXT,
                    start_time TEXT,
                    end_time TEXT,
                    UNIQUE(name, weekday)
                )''')
    conn.commit()
    conn.close()

# Wichtig: init_db() wird direkt beim Import ausgeführt
init_db()

@app.route("/")
def index():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT name, role, weekday, start_time, end_time FROM availability")
    entries = c.fetchall()
    conn.close()
    return render_template("index.html", entries=entries)

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form["name"]
    role = request.form["role"]
    weekday = request.form["weekday"]
    start_time = request.form["start_time"]
    end_time = request.form["end_time"]

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("REPLACE INTO availability (name, role, weekday, start_time, end_time) VALUES (?, ?, ?, ?, ?)",
              (name, role, weekday, start_time, end_time))
    conn.commit()
    conn.close()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
