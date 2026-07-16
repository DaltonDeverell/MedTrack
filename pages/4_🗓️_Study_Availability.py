import streamlit as st

from availability.availability import (
    load_grid,
    save_grid
)

# =====================================================
# PAGE
# =====================================================

st.set_page_config(
    page_title="Study Availability",
    page_icon="🗓️",
    layout="wide"
)

st.title("🗓️ Study Availability")

st.write(
    """
Select the times that you are happy to study.

Every green cell represents a **30 minute study slot**.

This timetable is automatically used by the planner and calendar.
"""
)

# =====================================================
# LOAD FROM DATABASE
# =====================================================

if "availability_grid" not in st.session_state:

    st.session_state.availability_grid = load_grid()

# =====================================================
# EDIT GRID
# =====================================================

edited_grid = st.data_editor(

    st.session_state.availability_grid,

    use_container_width=True,

    hide_index=False,

    num_rows="fixed",

    key="availability_editor"

)

# =====================================================
# AUTO SAVE
# =====================================================

if not edited_grid.equals(st.session_state.availability_grid):

    st.session_state.availability_grid = edited_grid

    save_grid(edited_grid)

    st.toast(
        "Availability saved",
        icon="✅"
    )

# =====================================================
# SUMMARY
# =====================================================

st.divider()

st.subheader("Weekly Summary")

total_slots = int(edited_grid.sum().sum())

total_hours = total_slots * 0.5

st.metric(

    "Available Study Time",

    f"{total_hours:.1f} hrs/week"

)

daily = edited_grid.sum(axis=0)

cols = st.columns(7)

for i, day in enumerate(daily.index):

    with cols[i]:

        st.metric(

            day[:3],

            f"{daily[day] * 30} min"

        )