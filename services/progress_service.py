from datetime import datetime

from services.supabase_client import supabase


# =====================================================
# CURRENT USER
# =====================================================

def get_current_user():

    response = supabase.auth.get_user()

    return response.user



# =====================================================
# USER ID
# =====================================================

def get_user_id():

    user = get_current_user()

    if user is None:
        return None

    return user.id



# =====================================================
# GET COMPLETED IDS
# =====================================================

def get_completed_ids():

    user_id = get_user_id()

    if user_id is None:
        return []


    response = (
        supabase
        .table("progress")
        .select("curriculum_id")
        .eq(
            "user_id",
            user_id
        )
        .eq(
            "completed",
            True
        )
        .execute()
    )


    return [
        int(row["curriculum_id"])
        for row in response.data
    ]



# =====================================================
# CHECK COMPLETED
# =====================================================

def is_completed(curriculum_id):

    user_id = get_user_id()

    if user_id is None:
        return False


    response = (
        supabase
        .table("progress")
        .select("completed")
        .eq(
            "user_id",
            user_id
        )
        .eq(
            "curriculum_id",
            curriculum_id
        )
        .limit(1)
        .execute()
    )


    if not response.data:

        return False


    return response.data[0]["completed"]



# =====================================================
# SET COMPLETED
# =====================================================

def set_completed(
    curriculum_id,
    completed
):

    user_id = get_user_id()

    if user_id is None:
        return



    existing = (
        supabase
        .table("progress")
        .select("id")
        .eq(
            "user_id",
            user_id
        )
        .eq(
            "curriculum_id",
            curriculum_id
        )
        .execute()
    )


    data = {

        "user_id": user_id,

        "curriculum_id": curriculum_id,

        "completed": completed,

        "completed_at":
            datetime.utcnow().isoformat()
            if completed
            else None

    }



    if existing.data:


        (
            supabase
            .table("progress")
            .update(data)
            .eq(
                "id",
                existing.data[0]["id"]
            )
            .execute()
        )


    else:


        (
            supabase
            .table("progress")
            .insert(data)
            .execute()
        )