from database import get_connection
from datetime import date

def register_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def add_subject(user_id, name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO subjects (user_id, name) VALUES (?, ?)", (user_id, name))
    conn.commit()
    conn.close()

def get_subjects(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM subjects WHERE user_id=?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def log_session(user_id, subject_id, duration_minutes, notes=""):
    conn = get_connection()
    cursor = conn.cursor()
    today = str(date.today())
    cursor.execute(
        "INSERT INTO sessions (user_id, subject_id, date, duration_minutes, notes) VALUES (?, ?, ?, ?, ?)",
        (user_id, subject_id, today, duration_minutes, notes)
    )
    conn.commit()
    conn.close()

def get_sessions(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.date, sub.name, s.duration_minutes, s.notes
        FROM sessions s
        JOIN subjects sub ON s.subject_id = sub.id
        WHERE s.user_id = ?
        ORDER BY s.date DESC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows