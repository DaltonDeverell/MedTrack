import streamlit as st
import sqlite3
from pathlib import Path

from database.database import create_database
from scheduler.importer import import_curriculum

# =====================================================
# PAGE SETTINGS
# =====================================================

st.set_page_config(
    page_title="MedTrack",
    page_icon="🩺",
    layout="wide"
)

# =====================================================
# DATABASE
# =====================================================

create_database()

DATABASE = "database/medtrack.db"

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

# Check whether curriculum already exists
cursor.execute("SELECT COUNT(*) FROM curriculum")
row_count = cursor.fetchone()[0]

conn.close()

# =====================================================
# IMPORT CURRICULUM (ONLY FIRST TIME)
# =====================================================

if row_count == 0:

    excel_files = sorted(
        f for f in Path("data").glob("*.xlsx")
        if not f.name.startswith("~$")
    )

    if excel_files:

        import_curriculum(
            excel_files[0],
            DATABASE
        )

# =====================================================
# DASHBOARD
# =====================================================

st.title("🩺 MedTrack")

st.header("Dashboard")

st.success("Welcome to MedTrack!")

st.write(
    """
Welcome to MedTrack.

Use the navigation on the left to access:

- 📚 Curriculum
- 🏥 Placements
- 📅 Planner

Your curriculum is only imported once.
Your progress is saved automatically.
"""
)

# =====================================================
# ADMIN
# =====================================================

st.divider()

with st.expander("⚙️ Admin"):

    st.caption(
        "Only use this if your Excel curriculum changes."
    )

    if st.button("Re-import Curriculum"):

        import_curriculum(
            excel_files[0],
            DATABASE
        )

        st.success("Curriculum imported successfully.")

        st.rerun()