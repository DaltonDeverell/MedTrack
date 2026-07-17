import sqlite3
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from services.supabase_client import supabase


# =====================================================
# SQLITE
# =====================================================

conn = sqlite3.connect(
    "database/medtrack.db"
)

conn.row_factory = sqlite3.Row


rows = conn.execute(
    """
    SELECT *
    FROM curriculum
    """
).fetchall()


print(
    f"Found {len(rows)} curriculum rows"
)


# =====================================================
# CURRENT USER
# =====================================================

user_id = "ded1505f-49b6-4e49-a275-3e2722f10dc1"


print(
    "Uploading for:",
    user_id
)


# =====================================================
# UPLOAD
# =====================================================

data = []


for row in rows:

    data.append(
        {
            "user_id": user_id,
            "module": row["module"],
            "learning_type": row["learning_type"],
            "topic": row["topic"],
            "task": row["task"],
            "completed": row["completed"],
        }
    )


response = (
    supabase
    .table("curriculum")
    .insert(data)
    .execute()
)


print("Uploaded!")
print(response)