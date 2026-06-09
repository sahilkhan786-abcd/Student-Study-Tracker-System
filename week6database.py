# Week 6 - SQLite Database Integration

import sqlite3
from datetime import date

DB = "study_tracker.db"

# Create tables
def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT,
            date TEXT,
            duration INTEGER,
            notes TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY,
            daily_goal INTEGER
        )
    """)
    conn.commit()
    conn.close()
    print("Database initialized. Tables created.")

def add_subject(name):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("INSERT INTO subjects (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()
    print(f"Subject added: {name}")

def log_session(subject, duration, notes):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    today = str(date.today())
    cur.execute("INSERT INTO sessions (subject, date, duration, notes) VALUES (?, ?, ?, ?)",
                (subject, today, duration, notes))
    conn.commit()
    conn.close()
    print(f"Session logged: {subject} for {duration} minutes")

def set_goal(minutes):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("DELETE FROM goals")
    cur.execute("INSERT INTO goals (id, daily_goal) VALUES (1, ?)", (minutes,))
    conn.commit()
    conn.close()
    print(f"Daily goal set: {minutes} minutes")

def get_goal():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT daily_goal FROM goals")
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 0

def show_sessions():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT subject, date, duration, notes FROM sessions")
    rows = cur.fetchall()
    conn.close()
    print("\nAll Sessions:")
    for r in rows:
        print(f"  Subject: {r[0]} | Date: {r[1]} | Duration: {r[2]} mins | Notes: {r[3]}")

# Testing
init_db()
add_subject("Mathematics")
add_subject("Python Programming")
log_session("Mathematics", 60, "Studied algebra")
log_session("Python Programming", 45, "Practiced functions")
set_goal(120)
show_sessions()
print(f"\nDaily Goal: {get_goal()} minutes")