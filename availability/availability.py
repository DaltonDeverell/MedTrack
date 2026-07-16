import sqlite3
import pandas as pd

DATABASE = "database/medtrack.db"

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
    "Sunday"
]

# =====================================================
# HALF HOUR TIME SLOTS
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
# DATABASE
# =====================================================

def get_connection():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn


# =====================================================
# CREATE TABLE
# =====================================================

def create_availability_table():

    conn = get_connection()

    conn.execute("""

        CREATE TABLE IF NOT EXISTS availability (

            day TEXT,

            time TEXT,

            available INTEGER,

            PRIMARY KEY(day,time)

        )

    """)

    conn.commit()

    conn.close()


# =====================================================
# EMPTY GRID
# =====================================================

def empty_grid():

    return pd.DataFrame(

        False,

        index=TIME_SLOTS,

        columns=DAYS

    )


# =====================================================
# LOAD GRID
# =====================================================

def load_grid():

    create_availability_table()

    grid = empty_grid()

    conn = get_connection()

    rows = conn.execute("""

        SELECT *

        FROM availability

    """).fetchall()

    conn.close()

    for row in rows:

        grid.loc[
            row["time"],
            row["day"]
        ] = bool(row["available"])

    return grid


# =====================================================
# SAVE GRID
# =====================================================

def save_grid(grid):

    create_availability_table()

    conn = get_connection()

    conn.execute("""

        DELETE FROM availability

    """)

    for day in DAYS:

        for time in TIME_SLOTS:

            conn.execute("""

                INSERT INTO availability

                VALUES (?,?,?)

            """,

            (

                day,

                time,

                int(grid.loc[time,day])

            )

            )

    conn.commit()

    conn.close()


# =====================================================
# GET AVAILABLE SLOTS
# =====================================================

def get_available_slots(day):

    grid = load_grid()

    available = []

    for time in TIME_SLOTS:

        if grid.loc[time,day]:

            available.append(time)

    return available