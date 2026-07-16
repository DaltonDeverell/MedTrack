import sqlite3
from datetime import datetime

from availability.availability import get_available_slots
from timetable.timetable_service import (
    load_blocks_for_day,
    remove_slots_inside_blocks
)

DATABASE = "database/medtrack.db"

# =====================================================
# STUDY DURATIONS (minutes)
# =====================================================

STUDY_TIMES = {

    "Lectures": 60,

    "Clinical Pharmacology": 30,

    "Online Modules": 45,

    "SDL": 45,

    "Videos": 30

}

# =====================================================
# LEARNING TYPES
# =====================================================

SELF_STUDY_TYPES = [

    "Lectures",

    "Clinical Pharmacology",

    "Online Modules",

    "SDL",

    "Videos"

]

ANKI_MINUTES = 45

# =====================================================
# TIME HELPERS
# =====================================================

def add_minutes(time_string, minutes):

    hour, minute = map(int, time_string.split(":"))

    total = hour * 60 + minute + minutes

    return f"{total // 60:02d}:{total % 60:02d}"


# =====================================================
# GENERATE PLAN
# =====================================================

# =====================================================
# GENERATE PLAN
# =====================================================

def generate_plan(module, hours):

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # -------------------------------------------------
    # Load curriculum
    # -------------------------------------------------

    if module == "All":

        cursor.execute("""
            SELECT *
            FROM curriculum
            WHERE completed = 0
            ORDER BY module,
                     learning_type,
                     topic,
                     task
        """)

    else:

        cursor.execute("""
            SELECT *
            FROM curriculum
            WHERE completed = 0
            AND module = ?
            ORDER BY learning_type,
                     topic,
                     task
        """, (module,))

    rows = cursor.fetchall()
    conn.close()

    # -------------------------------------------------
    # Keep self-study items
    # -------------------------------------------------

    tasks = [
        row
        for row in rows
        if row["learning_type"] in SELF_STUDY_TYPES
    ]

    grouped = {}

    for learning_type in SELF_STUDY_TYPES:
        grouped[learning_type] = []

    for task in tasks:
        grouped[task["learning_type"]].append(task)

    # -------------------------------------------------
    # Available study time
    # -------------------------------------------------

    today = datetime.today().strftime("%A")

    available_slots = get_available_slots(today)

    blocks = load_blocks_for_day(today)

    available_slots = remove_slots_inside_blocks(
        available_slots,
        blocks
    )

    if len(available_slots) == 0:
        available_slots = ["18:00"]

    available_minutes = min(
        len(available_slots) * 30,
        hours * 60
    )

    available_minutes -= ANKI_MINUTES

    if available_minutes < 0:
        available_minutes = 0

    used_minutes = 0
    todays_plan = []

    # -------------------------------------------------
    # Build today's study tasks
    # -------------------------------------------------

    while used_minutes < available_minutes:

        added = False

        for learning_type in SELF_STUDY_TYPES:

            if len(grouped[learning_type]) == 0:
                continue

            task = grouped[learning_type][0]

            duration = STUDY_TIMES.get(
                learning_type,
                45
            )

            if used_minutes + duration > available_minutes:
                continue

            todays_plan.append({

                "id": task["id"],
                "module": task["module"],
                "topic": task["topic"],
                "learning_type": task["learning_type"],
                "task": task["task"],
                "duration": duration

            })

            grouped[learning_type].pop(0)

            used_minutes += duration

            added = True

        if not added:
            break
            # -------------------------------------------------
    # Build calendar schedule
    # -------------------------------------------------

    schedule = []

    current = available_slots[0]

    schedule.append({

        "title": "🧠 Anki",

        "learning_type": "Anki",

        "start": current,

        "end": add_minutes(
            current,
            ANKI_MINUTES
        ),

        "duration": ANKI_MINUTES

    })

    current = add_minutes(
        current,
        ANKI_MINUTES
    )

    for task in todays_plan:

        end = add_minutes(
            current,
            task["duration"]
        )

        schedule.append({

            "title": task["task"],

            "learning_type": task["learning_type"],

            "start": current,

            "end": end,

            "duration": task["duration"],

            "module": task["module"],

            "topic": task["topic"]

        })

        current = end

    # -------------------------------------------------
    # Return plan
    # -------------------------------------------------

    return {

        "anki_minutes": ANKI_MINUTES,

        "curriculum_minutes": used_minutes,

        "total_minutes": ANKI_MINUTES + used_minutes,

        "tasks": todays_plan,

        "schedule": schedule

    }