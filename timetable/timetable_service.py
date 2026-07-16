from services.supabase_client import supabase
from auth.auth import current_user

# =====================================================
# CONSTANTS
# =====================================================

DAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]

BLOCK_TYPES = {
    "Placement": "#d9534f",
    "University": "#0275d8",
    "Study": "#5cb85c",
    "Work": "#f0ad4e",
    "Personal": "#8e44ad",
    "Sleep": "#555555"
}


# =====================================================
# GET USER ID
# =====================================================

def get_user_id():

    user = current_user()

    if user is None:
        raise Exception("No user is logged in.")

    return user.id


# =====================================================
# ADD BLOCK
# =====================================================

def add_block(
    day,
    start_time,
    end_time,
    block_type,
    title
):

    supabase.table("schedule_blocks").insert({

        "user_id": get_user_id(),

        "day": day,

        "start_time": start_time,

        "end_time": end_time,

        "block_type": block_type,

        "title": title,

        "colour": BLOCK_TYPES[block_type]

    }).execute()


# =====================================================
# LOAD ALL BLOCKS
# =====================================================

def load_blocks():

    response = (
        supabase
        .table("schedule_blocks")
        .select("*")
        .eq("user_id", get_user_id())
        .execute()
    )

    rows = response.data

    day_order = {
        "Monday": 1,
        "Tuesday": 2,
        "Wednesday": 3,
        "Thursday": 4,
        "Friday": 5,
        "Saturday": 6,
        "Sunday": 7
    }

    rows.sort(
        key=lambda x: (
            day_order[x["day"]],
            x["start_time"]
        )
    )

    return rows


# =====================================================
# LOAD ONE DAY
# =====================================================

def load_day(day):

    response = (
        supabase
        .table("schedule_blocks")
        .select("*")
        .eq("user_id", get_user_id())
        .eq("day", day)
        .order("start_time")
        .execute()
    )

    return response.data


# =====================================================
# DELETE BLOCK
# =====================================================

def delete_block(block_id):

    (
        supabase
        .table("schedule_blocks")
        .delete()
        .eq("id", block_id)
        .eq("user_id", get_user_id())
        .execute()
    )


# =====================================================
# UPDATE BLOCK
# =====================================================

def update_block(
    block_id,
    day,
    start_time,
    end_time,
    block_type,
    title
):

    (
        supabase
        .table("schedule_blocks")
        .update({

            "day": day,

            "start_time": start_time,

            "end_time": end_time,

            "block_type": block_type,

            "title": title,

            "colour": BLOCK_TYPES[block_type]

        })
        .eq("id", block_id)
        .eq("user_id", get_user_id())
        .execute()
    )


# =====================================================
# LOAD BLOCKS FOR ONE DAY
# =====================================================

def load_blocks_for_day(day):

    return load_day(day)


# =====================================================
# REMOVE BLOCKED STUDY SLOTS
# =====================================================

def remove_slots_inside_blocks(available_slots, blocks):

    remaining = []

    for slot in available_slots:

        blocked = False

        for block in blocks:

            if block["block_type"] == "Study":
                continue

            if block["start_time"] <= slot < block["end_time"]:
                blocked = True
                break

        if not blocked:
            remaining.append(slot)

    return remaining