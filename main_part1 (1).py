import streamlit as st
from datetime import date
from database import init_db, add_subject, get_subjects, log_session, set_goal, get_goal
import sqlite3

init_db()

DB = "study_tracker.db"

st.markdown("""
    <style>
        .main { background-color: #f5f7fa; }
        .block-container { padding-top: 2rem; }
        h1 { color: #1a1a2e; }
        h2, h3 { color: #16213e; }
        .stMetric { background-color: #ffffff; padding: 10px; border-radius: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); }
        .stButton>button { background-color: #0f3460; color: white; border-radius: 8px; padding: 8px 20px; border: none; }
        .stButton>button:hover { background-color: #e94560; color: white; }
    </style>
""", unsafe_allow_html=True)

st.title("Student Study Tracker System")

menu = st.sidebar.selectbox("Menu", [
    "Dashboard",
    "Log Session",
    "Manage Subjects",
    "Set Goal"
])

if menu == "Dashboard":
    st.header("Dashboard")

    from tracker import get_summary
    today_mins, goal, streak = get_summary()

    col1, col2, col3 = st.columns(3)
    col1.metric("Today's Study Time", f"{today_mins} mins")
    col2.metric("Daily Goal", f"{goal} mins")
    col3.metric("Streak", f"{streak} day(s)")

    st.subheader("Today's Goal Progress")
    if goal > 0:
        percent = min(today_mins / goal, 1.0)
        st.progress(percent)
        percent_display = round(percent * 100)
        if percent_display >= 100:
            st.success(f"Goal completed! You studied {today_mins} mins out of {goal} mins.")
        else:
            st.info(f"{percent_display}% of daily goal completed. {goal - today_mins} mins left.")
    else:
        st.warning("No daily goal set. Go to Set Goal to set one.")

elif menu == "Log Session":
    st.header("Log Study Session")
    subjects = get_subjects()

    if not subjects:
        st.warning("No subjects found. Please add subjects first.")
    else:
        subject_map = {name: sid for sid, name in subjects}
        subject_name = st.selectbox("Select Subject", list(subject_map.keys()))
        duration = st.number_input("Duration (minutes)", min_value=1, step=1)
        notes = st.text_input("Notes (optional)")

        if st.button("Save Session"):
            sid = subject_map[subject_name]
            log_session(sid, str(date.today()), duration, notes)
            st.success("Session logged!")

elif menu == "Manage Subjects":
    st.header("Manage Subjects")

    def delete_subject(subject_id):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute("DELETE FROM subjects WHERE id=?", (subject_id,))
        cur.execute("DELETE FROM sessions WHERE subject_id=?", (subject_id,))
        conn.commit()
        conn.close()

    new_subject = st.text_input("Enter subject name")
    if st.button("Add Subject"):
        if new_subject.strip():
            add_subject(new_subject.strip())
            st.success(f"Subject '{new_subject}' added!")
        else:
            st.error("Please enter a subject name.")

    st.subheader("Your Subjects")
    subjects = get_subjects()
    if subjects:
        for sid, name in subjects:
            col1, col2 = st.columns([4, 1])
            col1.write(f"- {name}")
            if col2.button("Delete", key=f"del_sub_{sid}"):
                delete_subject(sid)
                st.warning(f"Subject '{name}' and all its sessions deleted.")
                st.rerun()
    else:
        st.info("No subjects added yet.")

elif menu == "Set Goal":
    st.header("Set Daily Goal")
    current = get_goal()
    st.info(f"Current goal: {current} mins/day")
    goal_input = st.number_input("New daily goal (minutes)", min_value=1, step=1)

    if st.button("Save Goal"):
        set_goal(int(goal_input))
        st.success(f"Goal set to {goal_input} minutes per day!")