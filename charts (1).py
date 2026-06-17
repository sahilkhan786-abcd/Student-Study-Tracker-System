import matplotlib.pyplot as plt
from tracker import get_sessions, get_goal
from collections import defaultdict

def show_charts(user_id):
    sessions = get_sessions(user_id)

    if not sessions:
        import tkinter.messagebox as mb
        mb.showinfo("No Data", "No study sessions found. Log some sessions first.")
        return

    daily_mins = defaultdict(int)
    subject_mins = defaultdict(int)

    #Pie Chart
    for date, subject, duration, notes in sessions:
        daily_mins[date] += duration
        subject_mins[subject] += duration

    dates = sorted(daily_mins.keys())
    minutes = [daily_mins[d] for d in dates]
    goal = get_goal(user_id)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("Study Analytics", fontsize=16, fontweight="bold")

    #Bar Graph
    ax1.bar(dates, minutes, color="steelblue")
    if goal > 0:
        ax1.axhline(y=goal, color="red", linestyle="--", label=f"Goal: {goal} mins")
        ax1.legend()
    ax1.set_title("Daily Study Time")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Minutes")
    ax1.tick_params(axis="x", rotation=45)

    ax2.pie(
        subject_mins.values(),
        labels=subject_mins.keys(),
        autopct="%1.1f%%",
        startangle=140
    )
    ax2.set_title("Time per Subject")

    plt.tight_layout()
    plt.show()