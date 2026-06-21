import matplotlib.pyplot as plt
from tracker import get_daily_data, get_subject_data

def get_daily_chart(goal=0):
    daily = get_daily_data()

    if not daily:
        return None

    dates = sorted(daily.keys())
    mins = [daily[d] for d in dates]

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(dates, mins, color="steelblue")

    if goal > 0:
        ax.axhline(y=goal, color="red", linestyle="--", label=f"Goal: {goal} mins")
        ax.legend()

    ax.set_title("Daily Study Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Minutes")
    ax.tick_params(axis="x", rotation=45)
    plt.tight_layout()

    return fig

def get_subject_chart():
    subjects, mins = get_subject_data()

    if not subjects:
        return None

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(mins, labels=subjects, autopct="%1.1f%%", startangle=140)
    ax.set_title("Time Per Subject")
    plt.tight_layout()

    return fig