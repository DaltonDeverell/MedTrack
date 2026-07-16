from services.supabase_client import supabase


def load_blocks(user_id):

    response = (
        supabase
        .table("schedule_blocks")
        .select("*")
        .eq("user_id", user_id)
        .order("day")
        .order("start_time")
        .execute()
    )

    return response.data


def load_day(user_id, day):

    response = (
        supabase
        .table("schedule_blocks")
        .select("*")
        .eq("user_id", user_id)
        .eq("day", day)
        .order("start_time")
        .execute()
    )

    return response.data