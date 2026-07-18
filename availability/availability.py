from services.supabase_client import supabase
from services.progress_service import get_user_id
import pandas as pd

# =====================================================
# DAYS
# =====================================================

DAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

# =====================================================
# HALF HOUR SLOTS
# =====================================================

TIME_SLOTS = []

hour = 6
minute = 0

while True:

    TIME_SLOTS.append(
        f"{hour:02d}:{minute:02d}"
    )

    minute += 30

    if minute == 60:

        hour += 1
        minute = 0

    if hour == 22 and minute == 30:
        break


# =====================================================
# EMPTY GRID
# =====================================================

def empty_grid():

    return pd.DataFrame(
        False,
        index=TIME_SLOTS,
        columns=DAYS,
    )


# =====================================================
# LOAD GRID
# =====================================================

def load_grid():

    user_id = get_user_id()

    grid = empty_grid()

    if user_id is None:
        return grid

    response = (
        supabase
        .table("availability")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )

    for row in response.data:

        day = row["day"]
        time = row["time"]

        if (
            day in DAYS
            and time in TIME_SLOTS
        ):

            grid.loc[time, day] = row["available"]

    return grid
# =====================================================
# SAVE GRID
# =====================================================

def save_grid(grid):

    user_id = get_user_id()

    if user_id is None:
        return

    # Remove old availability

    (
        supabase
        .table("availability")
        .delete()
        .eq("user_id", user_id)
        .execute()
    )

    rows = []

    for day in DAYS:

        for time in TIME_SLOTS:

            rows.append({

                "user_id": user_id,

                "day": day,

                "time": time,

                "available": bool(
                    grid.loc[time, day]
                )

            })

    if rows:

        (
            supabase
            .table("availability")
            .insert(rows)
            .execute()
        )


# =====================================================
# GET AVAILABLE SLOTS
# =====================================================

def get_available_slots(day):

    grid = load_grid()

    available = []

    for time in TIME_SLOTS:

        if bool(grid.loc[time, day]):

            available.append(time)

    return available