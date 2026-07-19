from datetime import date

from services.supabase_client import supabase
from services.progress_service import get_user_id


def _today():
    return date.today().isoformat()


def get_today_plan():

    user_id = get_user_id()

    if user_id is None:
        return []

    response = (
        supabase
        .table("daily_plan")
        .select("""
            id,
            curriculum_id,
            duration,
            completed,
            task_order,
            curriculum (
                task,
                module,
                topic,
                learning_type
            )
        """)
        .eq("user_id", user_id)
        .eq("plan_date", _today())
        .order("task_order")
        .execute()
    )

    tasks = []

    for row in response.data:

        curriculum = row.get("curriculum")

        if curriculum:

            tasks.append({

                "id": row["curriculum_id"],
                "curriculum_id": row["curriculum_id"],
                "task": curriculum["task"],
                "module": curriculum["module"],
                "topic": curriculum["topic"],
                "learning_type": curriculum["learning_type"],
                "duration": row["duration"],
                "completed": row["completed"]

            })

    return tasks


def save_today_plan(tasks):

    user_id = get_user_id()

    if user_id is None:
        return

    today = _today()

    # Delete today's existing plan
    (
        supabase
        .table("daily_plan")
        .delete()
        .eq("user_id", user_id)
        .eq("plan_date", today)
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
            "plan_date": today,
            "curriculum_id": curriculum_id,
            "duration": task["duration"],
            "completed": False,
            "task_order": order

        })

    if rows:

        (
            supabase
            .table("daily_plan")
            .insert(rows)
            .execute()
        )


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
        .eq("plan_date", _today())
        .eq("curriculum_id", curriculum_id)
        .execute()
    )