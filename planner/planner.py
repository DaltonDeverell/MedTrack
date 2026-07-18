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

def generate_plan(module, hours, anki_minutes):

    query = (
        supabase
        .table("curriculum")
        .select(
            "id,module,topic,learning_type,task"
        )
    )

    if module != "All":
        query = query.eq("module", module)

    rows = query.execute().data or []

    completed_ids = set(get_completed_ids())

    tasks = []

    for row in rows:

        if (
            row["learning_type"] in SELF_STUDY_TYPES
            and row["id"] not in completed_ids
        ):
            tasks.append(row)

    available_minutes = max(
        0,
        (hours * 60) - anki_minutes,
    )

    used_minutes = 0

    todays_plan = []

    while used_minutes < available_minutes:

        added = False

        for task in tasks:

            duration = STUDY_TIMES.get(
                task["learning_type"],
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

            used_minutes += duration

            tasks.remove(task)

            added = True

            break

        if not added:
            break
            # =====================================================
    # BUILD SCHEDULE
    # =====================================================

    current = "09:00"

    schedule = []

    if anki_minutes > 0:

        end = add_minutes(current, anki_minutes)

        schedule.append({

            "title": "🧠 Anki",
            "learning_type": "Anki",
            "start": current,
            "end": end,
            "duration": anki_minutes,

        })

        current = end

    for task in todays_plan:

        end = add_minutes(current, task["duration"])

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

    # =====================================================
    # RETURN
    # =====================================================

    return {

        "anki_minutes": anki_minutes,

        "curriculum_minutes": used_minutes,

        "total_minutes": anki_minutes + used_minutes,

        "tasks": todays_plan,

        "schedule": schedule,

    }