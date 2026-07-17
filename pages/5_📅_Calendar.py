import streamlit as st
from auth.require_login import require_login

require_login()
from streamlit_calendar import calendar
from planner.planner import generate_plan
from timetable.timetable_service import load_blocks
from datetime import datetime, timedelta
import sqlite3

# =====================================================
# PAGE
# =====================================================

st.set_page_config(
    page_title="Study Calendar",
    page_icon="📅",
    layout="wide"
)

st.title("📅 Study Calendar")

st.write(
    "Visualise your personalised study plan."
)

# =====================================================
# LOAD MODULES
# =====================================================

conn = sqlite3.connect("database/medtrack.db")
conn.row_factory = sqlite3.Row

modules = conn.execute("""
SELECT DISTINCT module
FROM curriculum
ORDER BY module
""").fetchall()

conn.close()

module_names = ["All"] + [m["module"] for m in modules]

# =====================================================
# SETTINGS
# =====================================================

left, right = st.columns(2)

with left:


    if "selected_module" not in st.session_state:
        st.session_state["selected_module"] = "All"

    selected_module = st.selectbox(
        "Current Module / Placement",
        module_names,
        index=module_names.index(st.session_state["selected_module"])
    )

st.session_state["selected_module"] = selected_module

with right:

    hours = st.slider(
        "Study Hours Available",
        min_value=1,
        max_value=8,
        value=3
    )

# =====================================================
# GENERATE PLAN
# =====================================================

plan = generate_plan(
    selected_module,
    hours,
    0
)

# =====================================================
# COLOURS
# =====================================================

COLOURS = {

    "Anki": "#8e44ad",

    "Lectures": "#3498db",

    "Clinical Pharmacology": "#e67e22",

    "Online Modules": "#27ae60",

    "SDL": "#16a085",

    "Videos": "#e74c3c"

}

# =====================================================
# BUILD EVENTS
# =====================================================

events = []

today = datetime.now().date()

# =====================================================
# ADD RECURRING TIMETABLE EVENTS
# =====================================================

weekday_map = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6,
}

BLOCK_COLOURS = {
    "Placement": "#d63031",
    "University": "#0984e3",
    "Work": "#fdcb6e",
    "Personal": "#636e72",
}

today_weekday = today.weekday()

blocks = load_blocks()

for block in blocks:

    offset = weekday_map[block["day"]] - today_weekday

    event_date = today + timedelta(days=offset)

    start = datetime.fromisoformat(
        f"{event_date}T{block['start_time']}:00"
    )

    end = datetime.fromisoformat(
        f"{event_date}T{block['end_time']}:00"
    )

    events.append({

        "title": block["title"],

        "start": start.isoformat(),

        "end": end.isoformat(),

        "color": BLOCK_COLOURS.get(
            block["block_type"],
            "#555555"
        )

    })

for session in plan["schedule"]:

    start = datetime.fromisoformat(
        f"{today}T{session['start']}:00"
    )

    end = datetime.fromisoformat(
        f"{today}T{session['end']}:00"
    )

    events.append({

        "title": session["title"],

        "start": start.isoformat(),

        "end": end.isoformat(),

        "color": COLOURS.get(
            session["learning_type"],
            "#34495e"
        )

    })

# =====================================================
# CALENDAR OPTIONS
# =====================================================

calendar_options = {

    "initialView": "timeGridDay",

    "headerToolbar": {

        "left": "prev,next today",

        "center": "title",

        "right": "dayGridMonth,timeGridWeek,timeGridDay"

    },

    "slotMinTime": "06:00:00",

    "slotMaxTime": "23:00:00",

    "editable": False,

    "selectable": False,

    "height": 750

}

# =====================================================
# CSS
# =====================================================

custom_css = """

.fc-toolbar-title{
    font-size:28px;
    font-weight:bold;
}

.fc-event{
    border-radius:10px;
    border:none;
    font-weight:bold;
}

.fc-timegrid-slot{
    height:50px;
}

"""

# =====================================================
# DISPLAY CALENDAR
# =====================================================

calendar(
    events=events,
    options=calendar_options,
    custom_css=custom_css,
    key="study_calendar"
)

# =====================================================
# SUMMARY
# =====================================================

st.divider()

c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "🧠 Anki",
        f"{plan['anki_minutes']} min"
    )

with c2:
    st.metric(
        "📚 Study",
        f"{plan['curriculum_minutes']} min"
    )

with c3:
    st.metric(
        "⏱ Total",
        f"{plan['total_minutes']} min"
    )

# =====================================================
# TODAY'S SCHEDULE
# =====================================================

st.divider()

st.subheader("Today's Schedule")

for session in plan["schedule"]:

    st.markdown(
        f"""
**{session['title']}**

🕒 {session['start']} → {session['end']}

⏱ {session['duration']} minutes

---
"""
    )