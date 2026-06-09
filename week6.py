# Week 5 - Basic Project Structure with SQLite

import sqlite3

DB = "study_tracker.db"

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
    cur.execute("INSERT INTO sessions (subject, date, duration, notes) VALUES (?, ?, ?, ?)",
                (subject, "2026-06-05", duration, notes))
    conn.commit()
    conn.close()
    print(f"Session logged: {subject} for {duration} minutes")

def show_subjects():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM subjects")
    rows = cur.fetchall()
    conn.close()
    print("\nAll Subjects:")
    for r in rows:
        print(f"  ID: {r[0]} | Subject: {r[1]}")

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
add_subject("Mathematics")
add_subject("Python Programming")
add_subject("English")

show_subjects()

log_session("Mathematics", 60, "Studied algebra")
log_session("Python Programming", 45, "Practiced functions")

show_sessions()