import sqlite3
from pathlib import Path

# =====================================================
# DATABASE LOCATION
# =====================================================

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "medtrack.db"

# =====================================================
# CONNECTION
# =====================================================

def get_connection():

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    return conn


# =====================================================
# CREATE DATABASE
# =====================================================

def create_database():

    conn = get_connection()
    cursor = conn.cursor()

    # =================================================
    # CURRICULUM
    # =================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS curriculum (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            module TEXT NOT NULL,

            learning_type TEXT NOT NULL,

            topic TEXT,

            task TEXT NOT NULL,

            completed INTEGER DEFAULT 0

        )
    """)

    # =================================================
    # WEEKLY TIMETABLE
    # =================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schedule_blocks (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            day TEXT NOT NULL,

            start_time TEXT NOT NULL,

            end_time TEXT NOT NULL,

            block_type TEXT NOT NULL,

            title TEXT,

            colour TEXT

        )
    """)

    # =================================================
    # STUDY SESSIONS
    # =================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_sessions (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            session_date TEXT NOT NULL,

            task_id INTEGER,

            module TEXT,

            learning_type TEXT,

            topic TEXT,

            task TEXT,

            duration INTEGER,

            completed INTEGER DEFAULT 0

        )
    """)

    # =================================================
    # SETTINGS
    # =================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            setting TEXT UNIQUE,

            value TEXT

        )
    """)

    conn.commit()
    conn.close()