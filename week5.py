# Week 5 - Basic Project Structure

subjects = []
sessions = []

def add_subject(name):
    subjects.append(name)
    print(f"Subject added: {name}")

def log_session(subject, duration, notes):
    session = {
        "subject": subject,
        "duration": duration,
        "notes": notes
    }
    sessions.append(session)
    print(f"Session logged: {subject} for {duration} minutes")

def show_subjects():
    print("\nAll Subjects:")
    for s in subjects:
        print(f"  - {s}")

def show_sessions():
    print("\nAll Sessions:")
    for s in sessions:
        print(f"  Subject: {s['subject']} | Duration: {s['duration']} mins | Notes: {s['notes']}")

# Testing the functions
add_subject("Mathematics")
add_subject("Python Programming")
add_subject("English")

show_subjects()

log_session("Mathematics", 60, "Studied algebra")
log_session("Python Programming", 45, "Practiced functions")

show_sessions()