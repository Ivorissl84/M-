from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime, timedelta
from collections import defaultdict

app = Flask(__name__)

import os

# Sicherstellen, dass die Datenbank und Tabelle existiert
def init_db():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS availability (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            weekday TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

DB_NAME = "availability.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS availability (
            name TEXT,
            weekday TEXT,
            start_time TEXT,
            end_time TEXT,
            UNIQUE(name, weekday)
        )
        """)
        conn.commit()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["name"]
        weekday = request.form["weekday"]
        start_time = request.form["start_time"]
        end_time = request.form["end_time"]

        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("""
                INSERT OR REPLACE INTO availability (name, weekday, start_time, end_time)
                VALUES (?, ?, ?, ?)
            """, (name, weekday, start_time, end_time))
            conn.commit()

        return redirect("/")

    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM availability")
        data = c.fetchall()

    overlaps = find_overlaps(data)
    groups = generate_groups(data)
    return render_template("index.html", data=data, overlaps=overlaps, groups=groups)

def find_overlaps(entries):
    result = defaultdict(list)
    by_day = defaultdict(list)
    for name, day, start, end in entries:
        by_day[day].append((name, start, end))

    for day, entries in by_day.items():
        for i in range(len(entries)):
            name1, start1, end1 = entries[i]
            t1_start = datetime.strptime(start1, "%H:%M")
            t1_end = datetime.strptime(end1, "%H:%M")

            for j in range(i + 1, len(entries)):
                name2, start2, end2 = entries[j]
                t2_start = datetime.strptime(start2, "%H:%M")
                t2_end = datetime.strptime(end2, "%H:%M")

                latest_start = max(t1_start, t2_start)
                earliest_end = min(t1_end, t2_end)
                overlap = (earliest_end - latest_start).total_seconds() / 3600

                if overlap >= 2:
                    result[day].append((name1, name2, f"{overlap:.1f} Std"))
    return result

def generate_groups(entries):
    groups_by_day = defaultdict(list)
    by_day = defaultdict(list)

    for name, day, start, end in entries:
        by_day[day].append((name, start, end))

    for day, items in by_day.items():
        used = set()
        for i in range(len(items)):
            n1, s1, e1 = items[i]
            t1_start = datetime.strptime(s1, "%H:%M")
            t1_end = datetime.strptime(e1, "%H:%M")

            group = [n1]
            for j in range(len(items)):
                if i == j: continue
                n2, s2, e2 = items[j]
                if n2 in used or n1 in used:
                    continue

                t2_start = datetime.strptime(s2, "%H:%M")
                t2_end = datetime.strptime(e2, "%H:%M")

                latest_start = max(t1_start, t2_start)
                earliest_end = min(t1_end, t2_end)
                overlap = (earliest_end - latest_start).total_seconds() / 3600

                if overlap >= 2:
                    group.append(n2)

            if len(group) >= 2:
                group = sorted(set(group))
                if not any(set(group).issubset(set(g)) for g in groups_by_day[day]):
                    groups_by_day[day].append(group)
                    used.update(group)

    return groups_by_day

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
