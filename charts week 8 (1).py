import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from tracker import get_daily_data, get_subject_data

# Shared layout settings so every chart is transparent and theme-aware.
# Transparent backgrounds let the chart sit naturally on Streamlit's own
# light/dark card color instead of forcing white (which breaks dark mode).
# Font size bumped up for visibility on a projector / from the back of a room.
BASE_LAYOUT = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", size=15, color="#8b8fa3"),
    title_font=dict(size=20, family="Inter, sans-serif"),
    margin=dict(l=10, r=10, t=55, b=10),
)


def get_daily_chart(goal=0):
    data = get_daily_data()
    if not data or all(v == 0 for _, v in data):
        return None

    df = pd.DataFrame(data, columns=["date", "minutes"])
    df["date"] = pd.to_datetime(df["date"])

    colors = ["#6C63FF" if v < goal or goal == 0 else "#2ECC71" for v in df["minutes"]]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["date"], y=df["minutes"],
        marker_color=colors,
        name="Minutes studied",
        hovertemplate="%{x|%b %d}<br>%{y} mins<extra></extra>"
    ))

    if goal > 0:
        fig.add_hline(
            y=goal, line_dash="dash", line_color="#FF6B6B",
            annotation_text=f"Goal: {goal} mins",
            annotation_position="top right",
            annotation_font_color="#FF6B6B",
        )

    fig.update_layout(
        title="Daily Study Time (Last 30 Days)",
        xaxis_title="Date",
        yaxis_title="Minutes",
        height=380,
        **BASE_LAYOUT,
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(150,150,150,0.15)")
    return fig


def get_subject_chart():
    subjects, mins, colors = get_subject_data()
    if not subjects:
        return None

    fig = go.Figure(data=[go.Pie(
        labels=subjects,
        values=mins,
        hole=0.45,
        marker=dict(colors=colors, line=dict(color="rgba(0,0,0,0)", width=0)),
        textinfo="label+percent",
        textfont=dict(size=15, color="white"),
        hovertemplate="%{label}<br>%{value} mins<extra></extra>"
    )])

    fig.update_layout(
        title="Time Per Subject",
        height=380,
        showlegend=True,
        legend=dict(font=dict(color="#8b8fa3", size=15)),
        **BASE_LAYOUT,
    )
    return fig


def get_mini_week_chart():
    """A small sparkline-style chart for the dashboard preview."""
    data = get_daily_data()[-7:]
    if not data or all(v == 0 for _, v in data):
        return None

    df = pd.DataFrame(data, columns=["date", "minutes"])
    df["date"] = pd.to_datetime(df["date"])
    df["label"] = df["date"].dt.strftime("%a")

    fig = go.Figure(go.Bar(
        x=df["label"], y=df["minutes"],
        marker_color="#6C63FF",
        hovertemplate="%{x}<br>%{y} mins<extra></extra>"
    ))
    fig.update_layout(
        title="This Week",
        height=220,
        font=dict(size=10, color="#8b8fa3"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=5, r=5, t=30, b=5),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(150,150,150,0.15)")
    return fig


def get_subject_trend_chart(days=14):
    """Stacked bar chart: how each subject's daily time trends over time.
    Uses bars instead of an area fill because an area chart needs several
    spread-out days to show a visible shape -- with only 1-2 days of data
    it renders as an invisible sliver. Bars are visible from day one."""
    import sqlite3
    conn = sqlite3.connect("study_tracker.db")
    cur = conn.cursor()
    cur.execute(f"""
        SELECT s.date, sub.name, SUM(s.duration), sub.color
        FROM sessions s
        JOIN subjects sub ON s.subject_id = sub.id
        WHERE s.date >= date('now', '-{days} days')
        GROUP BY s.date, sub.name
        ORDER BY s.date
    """)
    rows = cur.fetchall()
    conn.close()

    if not rows:
        return None

    df = pd.DataFrame(rows, columns=["date", "subject", "minutes", "color"])
    df["date"] = pd.to_datetime(df["date"])
    color_map = dict(zip(df["subject"], df["color"]))

    fig = px.bar(
        df, x="date", y="minutes", color="subject",
        color_discrete_map=color_map,
        title=f"Subject Trend (Last {days} Days)",
        barmode="stack",
    )
    fig.update_layout(
        height=350,
        legend=dict(font=dict(color="#8b8fa3", size=15)),
        bargap=0.3,
        **BASE_LAYOUT,
    )
    fig.update_xaxes(
        showgrid=False,
        tickformat="%b %d",
        type="date",
    )
    fig.update_yaxes(showgrid=True, gridcolor="rgba(150,150,150,0.15)")
    return fig