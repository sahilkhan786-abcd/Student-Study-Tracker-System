from database import get_subject_totals, get_sessions, get_goal, get_today_total, get_streak
from datetime import date

def get_summary():
    today = str(date.today())
    today_mins = get_today_total(today)
    goal = get_goal()
    streak = get_streak()
    return today_mins, goal, streak

def get_ml_suggestion():
    data = get_subject_totals()

    if not data:
        return "No study data yet. Start logging sessions to get suggestions."

    if len(data) == 1:
        return f"You only have one subject so far. Keep studying {data[0][0]}!"

    sorted_data = sorted(data, key=lambda x: x[1])

    weakest = sorted_data[0][0]
    weakest_mins = sorted_data[0][1]
    strongest = sorted_data[-1][0]
    strongest_mins = sorted_data[-1][1]

    # Calculate average
    total = sum(mins for _, mins in data)
    average = total / len(data)

    suggestion = f"Based on your study history:\n\n"
    suggestion += f"You studied {strongest} the most ({strongest_mins} mins).\n"
    suggestion += f"You studied {weakest} the least ({weakest_mins} mins).\n\n"

    if weakest_mins < average * 0.5:
        suggestion += f"You really need to focus more on {weakest}. It is getting very little attention compared to your other subjects."
    else:
        suggestion += f"Try to spend a bit more time on {weakest} to keep things balanced."

    return suggestion

def get_daily_data():
    sessions = get_sessions()
    daily = {}
    for d, subject, duration, notes in sessions:
        daily[d] = daily.get(d, 0) + duration
    return daily

def get_subject_data():
    data = get_subject_totals()
    subjects = [row[0] for row in data]
    mins = [row[1] for row in data]
    return subjects, mins