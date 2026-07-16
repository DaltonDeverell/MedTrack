import sqlite3

DATABASE = "database/medtrack.db"


def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def get_dashboard_stats():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM curriculum")
    total = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM curriculum
        WHERE completed = 1
    """)
    completed = cursor.fetchone()[0]

    overall_progress = 0

    if total > 0:
        overall_progress = completed / total

    cursor.execute("""
        SELECT
            module,
            COUNT(*) as total,
            SUM(completed) as completed

        FROM curriculum

        GROUP BY module

        ORDER BY module
    """)

    modules = []

    for row in cursor.fetchall():

        module = row["module"]

        total_items = row["total"]

        completed_items = row["completed"] or 0

        progress = 0

        if total_items > 0:
            progress = completed_items / total_items

        modules.append({

            "module": module,
            "completed": completed_items,
            "total": total_items,
            "progress": progress

        })

    conn.close()

    return {

        "total": total,
        "completed": completed,
        "progress": overall_progress,
        "modules": modules

    }