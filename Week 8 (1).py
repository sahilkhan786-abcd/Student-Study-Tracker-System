from datetime import date
from database import (
    get_subject_totals, get_today_total, get_goal,
    get_streak, get_best_streak, get_goal_hit_days,
    get_daily_series, get_range_totals, get_subject_detail_stats
)

try:
    import numpy as np
    NUMPY_OK = True
except ImportError:
    NUMPY_OK = False


def get_summary():
    today = str(date.today())
    today_mins = get_today_total(today)
    goal = get_goal()
    streak = get_streak()
    best = get_best_streak()
    hit_days, total_days = get_goal_hit_days(7)
    return {
        "today_mins": today_mins,
        "goal": goal,
        "streak": streak,
        "best_streak": best,
        "goal_hit_days": hit_days,
        "goal_hit_total": total_days,
    }


def _normalize(values):
    """Min-max scale a list to 0-1, same idea as sklearn's MinMaxScaler."""
    if NUMPY_OK:
        arr = np.array(values, dtype=float)
        lo, hi = arr.min(), arr.max()
        if hi - lo == 0:
            return [0.5] * len(values)
        return list((arr - lo) / (hi - lo))
    lo, hi = min(values), max(values)
    if hi - lo == 0:
        return [0.5] * len(values)
    return [(v - lo) / (hi - lo) for v in values]


def get_ml_suggestion():
    """
    Multi-signal study coach.

    Instead of only comparing total minutes, this scores each subject on
    THREE normalized signals and blends them into one "attention score":

      1. total_minutes   -> how much total effort has gone in
      2. days_since_last  -> how stale / neglected it currently is
      3. distinct_days    -> how *consistently* (not just how much) it's studied

    A subject can have decent total minutes but still need attention if it
    was all crammed into one session three weeks ago -- that's the kind of
    pattern a single "lowest total" rule would miss entirely.
    """
    stats = get_subject_detail_stats()
    stats = [s for s in stats if s["session_count"] > 0 or True] 

    studied = [s for s in stats if s["session_count"] > 0]

    if not stats:
        return {"status": "empty", "message": (
            "No subjects yet. Add a few subjects and log some sessions \u2014 "
            "your personalized study plan will appear here once there's data to work with."
        )}

    if not studied:
        return {"status": "empty", "message": (
            "You've added subjects but haven't logged any sessions yet. "
            "Log your first session and this panel will start giving you real suggestions."
        )}

    if len(studied) == 1:
        only = studied[0]
        return {"status": "single", "message": (
            f"You're only tracking **{only['name']}** so far "
            f"({only['total_minutes']} mins across {only['session_count']} sessions). "
            "Add a second subject so I can compare and tell you where to focus."
        )}

    names = [s["name"] for s in studied]
    totals = [s["total_minutes"] for s in studied]
    staleness = [s["days_since_last"] if s["days_since_last"] is not None else 999 for s in studied]
    consistency = [s["distinct_days"] for s in studied]

    norm_total = _normalize(totals)              
    norm_staleness = _normalize(staleness)       
    norm_consistency = _normalize(consistency)   

    attention_scores = []
    for i in range(len(studied)):
        score = (
            0.40 * norm_total[i] +
            0.35 * (1 - norm_staleness[i]) +
            0.25 * norm_consistency[i]
        )
        attention_scores.append(score)

    ranked = sorted(
        zip(studied, attention_scores),
        key=lambda x: x[1]
    )

    weakest, weakest_score = ranked[0]
    strongest, strongest_score = ranked[-1]

    avg_total = sum(totals) / len(totals)
    never_mentioned = [s["name"] for s in stats if s["session_count"] == 0]
    stale_subjects = [s["name"] for s in studied if (s["days_since_last"] or 0) >= 4]
    one_session_wonders = [
        s["name"] for s in studied
        if s["session_count"] == 1 and s["total_minutes"] >= avg_total
    ]

    message = _build_coaching_message(
        weakest, strongest, avg_total, never_mentioned,
        stale_subjects, one_session_wonders
    )

    return {
        "status": "ok",
        "weakest": weakest["name"],
        "weakest_mins": weakest["total_minutes"],
        "strongest": strongest["name"],
        "strongest_mins": strongest["total_minutes"],
        "average": round(avg_total, 1),
        "neglected_recently": stale_subjects,
        "ranked": [
            (s["name"], s["total_minutes"], s["distinct_days"],
             s["days_since_last"], round(score * 100))
            for s, score in ranked
        ],
        "message": message,
    }


def _build_coaching_message(weakest, strongest, avg_total, never_mentioned, stale, one_session_wonders):
    parts = []

    days_since = weakest["days_since_last"]
    recency_phrase = (
        "today" if days_since == 0 else
        "yesterday" if days_since == 1 else
        f"{days_since} days ago" if days_since is not None else "a while back"
    )

    parts.append(
        f"**{weakest['name']}** needs your attention next. You last touched it "
        f"**{recency_phrase}**, with only **{weakest['total_minutes']} mins** logged "
        f"across **{weakest['distinct_days']} day(s)**."
    )

    if weakest["session_count"] == 1:
        parts.append(
            f"It's also only been studied in a single sitting \u2014 spreading it across "
            f"a few shorter sessions usually sticks better than one long cram."
        )

    parts.append(
        f"Meanwhile, **{strongest['name']}** is in good shape with "
        f"**{strongest['total_minutes']} mins** across **{strongest['distinct_days']} day(s)** \u2014 "
        f"keep that pace but don't let it crowd out the others."
    )

    if one_session_wonders and weakest["name"] not in one_session_wonders:
        names = ", ".join(f"**{n}**" for n in one_session_wonders)
        parts.append(
            f"Heads up: {names} {'looks' if len(one_session_wonders)==1 else 'look'} strong on total minutes, "
            f"but that time came from a single session. Real retention comes from spacing study out, "
            f"so plan a short follow-up session soon rather than trusting the total alone."
        )

    if never_mentioned:
        names = ", ".join(f"**{n}**" for n in never_mentioned)
        parts.append(f"You haven't logged anything yet for {names} \u2014 even a 10-minute first session will give me data to work with.")

    other_stale = [s for s in stale if s != weakest["name"]]
    if other_stale:
        names = ", ".join(f"**{n}**" for n in other_stale)
        parts.append(f"Also worth a look: {names} \u2014 it's been 4+ days since you last studied {'it' if len(other_stale)==1 else 'them'}.")

    return "\n\n".join(parts)


def get_daily_data():
    return get_daily_series(30)


def get_subject_data():
    data = get_subject_totals()
    subjects = [row[0] for row in data]
    mins = [row[1] for row in data]
    colors = [row[2] for row in data]
    return subjects, mins, colors