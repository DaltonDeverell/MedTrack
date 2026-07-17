import streamlit as st
# =====================================================
# GLOBAL SESSION STATE
# =====================================================

if "selected_module" not in st.session_state:
    st.session_state.selected_module = "All"
import sqlite3
from pathlib import Path

from auth.auth import login, signup, logout, current_user
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
# LOGIN
# =====================================================

user = current_user()

if user is None:

    st.title("🩺 MedTrack")

    st.subheader("Welcome")

    mode = st.radio(

        "Account",

        [

            "Login",

            "Create Account"

        ]

    )

    email = st.text_input("Email")

    password = st.text_input(

        "Password",

        type="password"

    )

    if st.button("Continue"):

        if mode == "Login":

            user = login(
                email,
                password
            )

        else:

            user = signup(
                email,
                password
            )

        if user:

            st.success("Success!")

            st.rerun()

    st.stop()

# =====================================================
# DATABASE
# =====================================================

create_database()

DATABASE = "database/medtrack.db"

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

cursor.execute(
    "SELECT COUNT(*) FROM curriculum"
)

row_count = cursor.fetchone()[0]

conn.close()

# =====================================================
# IMPORT CURRICULUM
# =====================================================

excel_files = sorted(

    f for f in Path("data").glob("*.xlsx")

    if not f.name.startswith("~$")

)

if row_count == 0 and excel_files:

    import_curriculum(

        excel_files[0],

        DATABASE

    )

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.success(

    f"Logged in as\n\n{user.email}"

)

if st.sidebar.button("🚪 Logout"):

    logout()

    st.rerun()

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

• 📚 Curriculum

• 🏥 Placements

• 📅 Planner

• 📆 Calendar

• 📖 Today

Your progress is automatically saved.
"""

)

# =====================================================
# ADMIN
# =====================================================

st.divider()

with st.expander("⚙️ Admin"):

    st.caption(

        "Only use this if your curriculum changes."

    )

    if st.button("Re-import Curriculum"):

        if excel_files:

            import_curriculum(

                excel_files[0],

                DATABASE

            )

            st.success(

                "Curriculum imported."

            )

            st.rerun()