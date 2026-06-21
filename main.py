import streamlit as st
from datetime import date
import pandas as pd

from database import (
    init_db, add_subject, get_subjects, get_subject_color_map,
    delete_subject, rename_subject,
    log_session, get_sessions, delete_session, update_session,
    set_goal, get_goal, get_range_totals
)
from tracker import get_summary, get_ml_suggestion
from charts import get_daily_chart, get_subject_chart, get_mini_week_chart, get_subject_trend_chart

st.set_page_config(
    page_title="Study Tracker",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

init_db()


st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
        font-size: 17px;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1300px;
    }

    /* Hero header -- gradient looks identical in both themes on purpose */
    .hero {
        background: linear-gradient(135deg, #6C63FF 0%, #4834d4 100%);
        padding: 28px 32px;
        border-radius: 18px;
        color: white;
        margin-bottom: 22px;
        box-shadow: 0 8px 24px rgba(108, 99, 255, 0.25);
    }
    .hero h1 {
        color: white;
        margin: 0;
        font-size: 36px;
        font-weight: 800;
    }
    .hero p {
        color: rgba(255,255,255,0.9);
        margin: 6px 0 0 0;
        font-size: 17px;
        font-weight: 500;
    }

    /* Metric cards -- use theme variable so dark mode gets a dark card,
       not a forced white box. Bumped up for back-of-room visibility. */
    div[data-testid="stMetric"] {
        background: var(--secondary-background-color);
        padding: 18px 18px;
        border-radius: 14px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
        border: 1px solid rgba(128,128,128,0.15);
    }
    div[data-testid="stMetricLabel"] {
        font-weight: 700;
        font-size: 16px !important;
    }
    div[data-testid="stMetricValue"] {
        font-weight: 800;
        font-size: 30px !important;
    }

    /* Section headers -- subheaders inside cards */
    h2, h3 {
        font-size: 24px !important;
        font-weight: 800 !important;
    }

    /* Body text, labels, captions -- bumped for readability from afar */
    p, label, .stMarkdown, div[data-testid="stText"] {
        font-size: 17px !important;
    }
    .stCaption, [data-testid="stCaptionContainer"] {
        font-size: 15px !important;
        font-weight: 500 !important;
    }

    /* Buttons -- bigger text, bigger padding */
    .stButton>button {
        background: linear-gradient(135deg, #6C63FF, #4834d4);
        color: white;
        border-radius: 10px;
        padding: 12px 26px;
        border: none;
        font-weight: 700;
        font-size: 17px;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        box-shadow: 0 4px 14px rgba(108, 99, 255, 0.4);
        transform: translateY(-1px);
    }
    .stButton>button p {
        font-size: 17px !important;
        font-weight: 700 !important;
    }

    /* Container "cards" -- targets st.container(border=True) directly,
       so there is no stray empty <div> sitting in the layout. */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 16px !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }

    .insight-box {
        background: linear-gradient(135deg, rgba(255,217,61,0.15), rgba(255,217,61,0.06));
        border-left: 5px solid #FFD93D;
        border-radius: 12px;
        padding: 20px 24px;
        font-size: 18px;
        font-weight: 500;
        line-height: 1.7;
    }

    /* Subject tags -- much bigger and bolder so they're readable on
       a projector screen from the back of a room */
    .tag {
        display: inline-block;
        padding: 7px 18px;
        border-radius: 24px;
        font-size: 16px;
        font-weight: 800;
        color: white;
        margin-right: 8px;
        letter-spacing: 0.3px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.15);
    }

    /* Tabs -- bigger, bolder, easier to read which one is active */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: var(--secondary-background-color);
        padding: 8px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 14px 22px;
        font-weight: 700;
        font-size: 18px;
    }
    .stTabs [data-baseweb="tab"] p {
        font-size: 18px !important;
        font-weight: 700 !important;
    }
    .stTabs [aria-selected="true"] {
        background: #6C63FF !important;
        color: white !important;
    }

    /* Inputs -- bigger text inside text boxes, number inputs, selects */
    .stTextInput input, .stNumberInput input, .stTextArea textarea,
    .stSelectbox div[data-baseweb="select"] {
        font-size: 17px !important;
    }

    /* Dataframes / tables */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        font-size: 16px !important;
    }

    /* Expander headers (session history rows) */
    .streamlit-expanderHeader, [data-testid="stExpander"] summary {
        font-size: 17px !important;
        font-weight: 600 !important;
    }

    /* Alert boxes (info/success/warning/error) */
    div[data-testid="stAlert"] p {
        font-size: 17px !important;
        font-weight: 500 !important;
    }
</style>
""", unsafe_allow_html=True)


summary = get_summary()

st.markdown("""
<div class="hero">
    <h1>📚 Student Study Tracker</h1>
    <p>Track your sessions, hit your goals, and let data guide your next move.</p>
</div>
""", unsafe_allow_html=True)

badge_cols = st.columns(5)
badge_cols[0].metric("⏱️ Today", f"{summary['today_mins']} min")
badge_cols[1].metric("🎯 Daily Goal", f"{summary['goal']} min")
badge_cols[2].metric("🔥 Current Streak", f"{summary['streak']} days")
badge_cols[3].metric("🏆 Best Streak", f"{summary['best_streak']} days")
badge_cols[4].metric("✅ Goal Hit (7d)", f"{summary['goal_hit_days']}/{summary['goal_hit_total']}")

st.write("")


tab1, tab2, tab3, tab4 = st.tabs([
    "🏠  Dashboard", "📝  Study Log", "⚙️  Subjects & Goals", "🧠  Insights"
])

with tab1:
    left, right = st.columns([1.3, 1])

    with left:
        with st.container(border=True):
            st.subheader("Today's Goal Progress")
            goal = summary["goal"]
            today_mins = summary["today_mins"]

            if goal > 0:
                percent = min(today_mins / goal, 1.0)
                st.progress(percent)
                pct_display = round(percent * 100)
                if pct_display >= 100:
                    st.success(f"🎉 Goal smashed! {today_mins} / {goal} mins done.")
                else:
                    st.info(f"{pct_display}% complete — {goal - today_mins} mins left to hit today's goal.")
            else:
                st.warning("No daily goal set yet. Head to **Subjects & Goals** to set one.")

        with st.container(border=True):
            st.subheader("⚡ Quick Log")
            subjects = get_subjects()
            if not subjects:
                st.warning("Add a subject first in **Subjects & Goals** to start logging.")
            else:
                qcol1, qcol2, qcol3 = st.columns([2, 1, 1])
                subject_map = {name: sid for sid, name, _ in subjects}
                with qcol1:
                    q_subject = st.selectbox("Subject", list(subject_map.keys()), key="quick_subject")
                with qcol2:
                    q_duration = st.number_input("Minutes", min_value=1, step=5, value=30, key="quick_duration")
                with qcol3:
                    st.write("")
                    st.write("")
                    if st.button("Log it ✅", key="quick_log_btn", use_container_width=True):
                        log_session(subject_map[q_subject], str(date.today()), int(q_duration), "")
                        st.success(f"Logged {q_duration} mins of {q_subject}!")
                        st.rerun()

    with right:
        with st.container(border=True):
            mini_chart = get_mini_week_chart()
            if mini_chart:
                st.plotly_chart(mini_chart, use_container_width=True, config={"displayModeBar": False})
            else:
                st.subheader("This Week")
                st.caption("No sessions logged yet this week.")

    with st.container(border=True):
        st.subheader("🕓 Recent Sessions")
        sessions = get_sessions()[:5]
        if not sessions:
            st.caption("Nothing logged yet — your most recent sessions will show up here.")
        else:
            for sid, d, subject, duration, notes, color in sessions:
                c1, c2 = st.columns([1, 4])
                c1.markdown(f'<span class="tag" style="background:{color}">{subject}</span>', unsafe_allow_html=True)
                c2.write(f"{d} · **{duration} mins**" + (f" · _{notes}_" if notes else ""))

with tab2:
    log_col, hist_col = st.columns([1, 1.4])

    with log_col:
        with st.container(border=True):
            st.subheader("Log a Study Session")
            subjects = get_subjects()
            if not subjects:
                st.warning("No subjects yet. Add one in **Subjects & Goals**.")
            else:
                subject_map = {name: sid for sid, name, _ in subjects}
                subject_name = st.selectbox("Subject", list(subject_map.keys()))
                duration = st.number_input("Duration (minutes)", min_value=1, step=5, value=30)
                notes = st.text_area("Notes (optional)", height=80, placeholder="What did you cover?")

                if st.button("Save Session", use_container_width=True):
                    log_session(subject_map[subject_name], str(date.today()), int(duration), notes)
                    st.success("Session saved!")
                    st.rerun()

    with hist_col:
        with st.container(border=True):
            st.subheader("Session History")
            sessions = get_sessions()

            if not sessions:
                st.info("No sessions logged yet.")
            else:
                subjects = get_subjects()
                subject_names = ["All"] + [name for _, name, _ in subjects]

                fcol1, fcol2 = st.columns(2)
                filter_subject = fcol1.selectbox("Filter by subject", subject_names)
                filter_date = fcol2.date_input("Filter by date", value=None)

                filtered = sessions
                if filter_subject != "All":
                    filtered = [s for s in filtered if s[2] == filter_subject]
                if filter_date:
                    filtered = [s for s in filtered if s[1] == str(filter_date)]

                if not filtered:
                    st.warning("No sessions match this filter.")
                else:
                    for sid, d, subject, duration, notes, color in filtered:
                        with st.expander(f"{d} — {subject} ({duration} mins)"):
                            st.markdown(f'<span class="tag" style="background:{color}">{subject}</span>', unsafe_allow_html=True)
                            new_duration = st.number_input("Minutes", min_value=1, value=duration, key=f"dur_{sid}")
                            new_notes = st.text_input("Notes", value=notes or "", key=f"notes_{sid}")
                            bcol1, bcol2 = st.columns(2)
                            if bcol1.button("💾 Update", key=f"upd_{sid}", use_container_width=True):
                                update_session(sid, new_duration, new_notes)
                                st.success("Updated!")
                                st.rerun()
                            if bcol2.button("🗑️ Delete", key=f"del_{sid}", use_container_width=True):
                                delete_session(sid)
                                st.warning("Deleted.")
                                st.rerun()

with tab3:
    sub_col, goal_col = st.columns([1, 1])

    with sub_col:
        with st.container(border=True):
            st.subheader("📘 Manage Subjects")
            new_subject = st.text_input("New subject name", placeholder="e.g. Data Structures")
            if st.button("Add Subject", use_container_width=True):
                if new_subject.strip():
                    ok = add_subject(new_subject.strip())
                    if ok:
                        st.success(f"Added '{new_subject}'!")
                        st.rerun()
                    else:
                        st.error("That subject already exists.")
                else:
                    st.error("Enter a subject name first.")

            st.write("")
            subjects = get_subjects()
            if subjects:
                for sid, name, color in subjects:
                    c1, c2, c3 = st.columns([3, 1, 1])
                    c1.markdown(f'<span class="tag" style="background:{color}">{name}</span>', unsafe_allow_html=True)
                    if c2.button("✏️", key=f"ren_{sid}"):
                        st.session_state[f"editing_{sid}"] = True
                    if c3.button("🗑️", key=f"delsub_{sid}"):
                        delete_subject(sid)
                        st.warning(f"Deleted '{name}' and its sessions.")
                        st.rerun()
                    if st.session_state.get(f"editing_{sid}"):
                        new_name = st.text_input("Rename to:", value=name, key=f"newname_{sid}")
                        if st.button("Save name", key=f"savename_{sid}"):
                            rename_subject(sid, new_name.strip())
                            st.session_state[f"editing_{sid}"] = False
                            st.rerun()
            else:
                st.caption("No subjects yet — add your first one above.")

    with goal_col:
        with st.container(border=True):
            st.subheader("🎯 Daily Study Goal")
            current_goal = get_goal()
            st.info(f"Current goal: **{current_goal} mins/day**")
            new_goal = st.number_input("Set new daily goal (minutes)", min_value=5, step=5, value=max(current_goal, 30))
            if st.button("Save Goal", use_container_width=True):
                set_goal(int(new_goal))
                st.success(f"Daily goal set to {new_goal} mins!")
                st.rerun()

            st.write("")
            st.subheader("📅 This Week's Goal Hits")
            hit, total = summary["goal_hit_days"], summary["goal_hit_total"]
            st.progress(hit / total if total else 0)
            st.caption(f"You hit your goal on **{hit} of the last {total} days**.")

with tab4:
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        with st.container(border=True):
            daily_chart = get_daily_chart(summary["goal"])
            if daily_chart:
                st.plotly_chart(daily_chart, use_container_width=True, config={"displayModeBar": False})
            else:
                st.subheader("Daily Study Time")
                st.caption("Log a few sessions to see your daily trend here.")

    with chart_col2:
        with st.container(border=True):
            subject_chart = get_subject_chart()
            if subject_chart:
                st.plotly_chart(subject_chart, use_container_width=True, config={"displayModeBar": False})
            else:
                st.subheader("Time Per Subject")
                st.caption("Log sessions across subjects to see the breakdown here.")

    with st.container(border=True):
        trend_chart = get_subject_trend_chart(14)
        if trend_chart:
            st.plotly_chart(trend_chart, use_container_width=True, config={"displayModeBar": False})
        else:
            st.subheader("Subject Trend")
            st.caption("Once you've logged sessions across a few days, your trend line appears here.")

    with st.container(border=True):
        st.subheader("🧠 Smart Suggestion")
        suggestion = get_ml_suggestion()

        st.markdown(f'<div class="insight-box">{suggestion["message"]}</div>', unsafe_allow_html=True)

        if suggestion["status"] == "ok":
            st.write("")
            st.caption("Subject ranking — lower score means it needs more attention (scaled 0–100):")
            rank_df = pd.DataFrame(
                suggestion["ranked"],
                columns=["Subject", "Total Minutes", "Days Studied", "Days Since Last", "Attention Score"]
            )
            st.dataframe(rank_df, use_container_width=True, hide_index=True)

st.write("")
with st.expander("📊 Weekly & Monthly Reports"):
    rcol1, rcol2 = st.columns(2)

    with rcol1:
        st.subheader("Last 7 Days")
        data = get_range_totals(7)
        if not data:
            st.caption("No sessions in the last 7 days.")
        else:
            df = pd.DataFrame(data, columns=["Subject", "Total Minutes"])
            st.metric("Total this week", f"{df['Total Minutes'].sum()} mins")
            st.dataframe(df, use_container_width=True, hide_index=True)

    with rcol2:
        st.subheader("Last 30 Days")
        data = get_range_totals(30)
        if not data:
            st.caption("No sessions in the last 30 days.")
        else:
            df = pd.DataFrame(data, columns=["Subject", "Total Minutes"])
            st.metric("Total this month", f"{df['Total Minutes'].sum()} mins")
            st.dataframe(df, use_container_width=True, hide_index=True)

st.write("")
st.caption("Student Study Tracker System · Built with Streamlit, SQLite, Plotly & scikit-learn")