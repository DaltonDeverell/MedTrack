from datetime import date

from services.supabase_client import supabase
from services.progress_service import get_user_id


def today():
    return date.today().isoformat()


# =====================================================
# LOAD TODAY'S PLAN
# =====================================================

def get_today_plan():

    user_id = get_user_id()

    if user_id is None:
        return []

    response = (
        supabase
        .table("daily_plan")
        .select("""
            curriculum_id,
            duration,
            completed,
            task_order,
            curriculum(
                task,
                module,
                topic,
                learning_type
            )
        """)
        .eq("user_id", user_id)
        .eq("plan_date", today())
        .order("task_order")
        .execute()
    )

    tasks = []

    for row in response.data or []:

        c = row["curriculum"]

        tasks.append({

            "id": row["curriculum_id"],
            "curriculum_id": row["curriculum_id"],
            "task": c["task"],
            "module": c["module"],
            "topic": c["topic"],
            "learning_type": c["learning_type"],
            "duration": row["duration"],
            "completed": row["completed"],

        })

    return tasks


# =====================================================
# SAVE TODAY'S PLAN
# =====================================================

def save_today_plan(tasks):

    user_id = get_user_id()

    if user_id is None:
        return

    # Delete ALL existing plans for this user
    (
        supabase
        .table("daily_plan")
        .delete()
        .eq("user_id", user_id)
        .execute()
    )

    rows = []
    seen = set()

    for order, task in enumerate(tasks, start=1):

        curriculum_id = task["curriculum_id"]

        if curriculum_id in seen:
            continue

        seen.add(curriculum_id)

        rows.append({

            "user_id": user_id,
            "plan_date": today(),
            "curriculum_id": curriculum_id,
            "duration": task["duration"],
            "completed": False,
            "task_order": order,

        })

    if rows:

        (
            supabase
            .table("daily_plan")
            .insert(rows)
            .execute()
        )


# =====================================================
# COMPLETE TASK
# =====================================================

def set_today_completed(curriculum_id, completed):

    user_id = get_user_id()

    if user_id is None:
        return

    (
        supabase
        .table("daily_plan")
        .update({
            "completed": completed
        })
        .eq("user_id", user_id)
        .eq("plan_date", today())
        .eq("curriculum_id", curriculum_id)
        .execute()
    )