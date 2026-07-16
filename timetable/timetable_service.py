import sqlite3

DATABASE = "database/medtrack.db"

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
# CONNECTION
# =====================================================

def get_connection():

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    return conn


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

    conn = get_connection()

    conn.execute("""

        INSERT INTO schedule_blocks

        (

            day,

            start_time,

            end_time,

            block_type,

            title,

            colour

        )

        VALUES

        (

            ?,?,?,?,?,?

        )

    """,

    (

        day,

        start_time,

        end_time,

        block_type,

        title,

        BLOCK_TYPES[block_type]

    )

    )

    conn.commit()

    conn.close()


# =====================================================
# LOAD BLOCKS
# =====================================================

def load_blocks():

    conn = get_connection()

    rows = conn.execute("""

        SELECT *

        FROM schedule_blocks

        ORDER BY

            CASE day

                WHEN 'Monday' THEN 1

                WHEN 'Tuesday' THEN 2

                WHEN 'Wednesday' THEN 3

                WHEN 'Thursday' THEN 4

                WHEN 'Friday' THEN 5

                WHEN 'Saturday' THEN 6

                WHEN 'Sunday' THEN 7

            END,

            start_time

    """).fetchall()

    conn.close()

    return rows


# =====================================================
# LOAD DAY
# =====================================================

def load_day(day):

    conn = get_connection()

    rows = conn.execute("""

        SELECT *

        FROM schedule_blocks

        WHERE day=?

        ORDER BY start_time

    """,(day,)).fetchall()

    conn.close()

    return rows


# =====================================================
# DELETE BLOCK
# =====================================================

def delete_block(block_id):

    conn = get_connection()

    conn.execute("""

        DELETE

        FROM schedule_blocks

        WHERE id=?

    """,(block_id,))

    conn.commit()

    conn.close()


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

    conn = get_connection()

    conn.execute("""

        UPDATE schedule_blocks

        SET

            day=?,

            start_time=?,

            end_time=?,

            block_type=?,

            title=?,

            colour=?

        WHERE id=?

    """,(

        day,

        start_time,

        end_time,

        block_type,

        title,

        BLOCK_TYPES[block_type],

        block_id

    ))

    conn.commit()

    conn.close()
    # =====================================================
# LOAD BLOCKS FOR ONE DAY
# =====================================================

def load_blocks_for_day(day):

    conn = get_connection()

    rows = conn.execute(
        """
        SELECT *
        FROM schedule_blocks
        WHERE day = ?
        ORDER BY start_time
        """,
        (day,)
    ).fetchall()

    conn.close()

    return rows


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