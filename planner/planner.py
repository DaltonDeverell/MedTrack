from datetime import datetime
import streamlit as st

from availability.availability import get_available_slots
from timetable.timetable_service import (
    load_blocks_for_day,
    remove_slots_inside_blocks,
)

from services.progress_service import get_completed_ids
from services.supabase_client import supabase


# =====================================================
# STUDY DURATIONS
# =====================================================

STUDY_TIMES = {
    "Lectures": 60,
    "Clinical Pharmacology": 30,
    "Online Modules": 45,
    "SDL": 45,
    "Videos": 30,
}


# =====================================================
# SELF STUDY TYPES
# =====================================================

SELF_STUDY_TYPES = [
    "Lectures",
    "Clinical Pharmacology",
    "Online Modules",
    "SDL",
    "Videos",
]


# =====================================================
# TIME HELPER
# =====================================================

def add_minutes(time_string, minutes):

    hour, minute = map(int, time_string.split(":"))

    total = hour * 60 + minute + minutes

    return f"{total // 60:02d}:{total % 60:02d}"


# =====================================================
# GENERATE PLAN
# =====================================================

def generate_plan(
    module,
    hours,
    anki_minutes,
):



    # -------------------------------------------------
    # LOAD CURRICULUM FROM SUPABASE
    # -------------------------------------------------

    query = (
        supabase
        .table("curriculum")
        .select("""
            id,
            module,
            topic,
            learning_type,
            task
        """)
    )

    if module != "All":

        query = query.eq(
            "module",
            module
        )

    response = query.execute()

    rows = response.data

    completed_ids = set(
        get_completed_ids()
    )

    # -------------------------------------------------
    # FILTER INCOMPLETE TASKS
    # -------------------------------------------------

    tasks = [
        row
        for row in rows
        if (
            row["learning_type"] in SELF_STUDY_TYPES
            and row["id"] not in completed_ids
        )
    ]

    grouped = {
        learning_type: []
        for learning_type in SELF_STUDY_TYPES
    }

    for task in tasks:
        grouped[task["learning_type"]].append(task)

    # -------------------------------------------------
    # GET AVAILABLE TIME
    # -------------------------------------------------

    today = datetime.today().strftime("%A")

    available_slots = get_available_slots(today)

    blocks = load_blocks_for_day(today)

    available_slots = remove_slots_inside_blocks(
        available_slots,
        blocks,
    )

    if len(available_slots) == 0:

        return {

            "anki_minutes": anki_minutes,

            "curriculum_minutes": 0,

            "total_minutes": anki_minutes,

            "tasks": [],

            "schedule": [],

        }

    available_minutes = min(
        len(available_slots) * 30,
        hours * 60,
    )


    available_minutes -= anki_minutes


    if available_minutes < 0:

        available_minutes = 0


    used_minutes = 0

    todays_plan = []

    # -------------------------------------------------
    # BUILD STUDY PLAN
    # -------------------------------------------------

    while used_minutes < available_minutes:

        added = False

        for learning_type in SELF_STUDY_TYPES:

            if not grouped[learning_type]:
                continue

            task = grouped[learning_type][0]

            duration = STUDY_TIMES.get(
                learning_type,
                45,
            )

            if used_minutes + duration > available_minutes:
                continue

            todays_plan.append({

                "id": task["id"],
                "curriculum_id": task["id"],
                "module": task["module"],
                "topic": task["topic"],
                "learning_type": task["learning_type"],
                "task": task["task"],
                "duration": duration,

            })

            grouped[learning_type].pop(0)

            used_minutes += duration

            added = True

        if not added:
            break


    # -------------------------------------------------
    # BUILD SCHEDULE
    # -------------------------------------------------

    schedule = []

    current = available_slots[0]

    if anki_minutes > 0:

        schedule.append({

            "title": "🧠 Anki",

            "learning_type": "Anki",

            "start": current,

            "end": add_minutes(
                current,
                anki_minutes,
            ),

            "duration": anki_minutes,

        })

        current = add_minutes(
            current,
            anki_minutes,
        )

    for task in todays_plan:

        end = add_minutes(
            current,
            task["duration"],
        )

        schedule.append({

            "title": task["task"],

            "learning_type": task["learning_type"],

            "start": current,

            "end": end,

            "duration": task["duration"],

            "module": task["module"],

            "topic": task["topic"],

        })

        current = end

    # -------------------------------------------------
    # RETURN
    # -------------------------------------------------

    return {

        "anki_minutes": anki_minutes,

        "curriculum_minutes": used_minutes,

        "total_minutes": anki_minutes + used_minutes,

        "tasks": todays_plan,

        "schedule": schedule,

    }