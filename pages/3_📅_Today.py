import streamlit as st

from auth.require_login import require_login
from planner.planner import generate_plan

from services.progress_service import (
    set_completed,
)

from services.daily_plan_service import (
    get_today_plan,
    save_today_plan,
    set_today_completed,
)

from services.supabase_client import supabase


require_login()


# =====================================================
# PAGE
# =====================================================

st.set_page_config(
    page_title="Today's Study",
    page_icon="📅",
    layout="wide",
)

st.title("📅 Today's Study")

st.write(
    "Generate today's personalised study schedule."
)


# =====================================================
# LOAD MODULES
# =====================================================

modules = (
    supabase
    .table("curriculum")
    .select("module")
    .execute()
    .data
)

module_names = ["All"]

for row in modules:

    module = row["module"]

    if module not in module_names:
        module_names.append(module)


# =====================================================
# HELPERS
# =====================================================

SECONDS_PER_CARD = 6
MAX_CARDS = 600


def prepare_plan(tasks):

    cleaned = []

    for task in tasks:

        task["curriculum_id"] = task.get(
            "curriculum_id",
            task["id"],
        )

        cleaned.append(task)

    return cleaned


# =====================================================
# SESSION STATE
# =====================================================

if "selected_module" not in st.session_state:
    st.session_state.selected_module = "All"

if "study_hours" not in st.session_state:
    st.session_state.study_hours = 3

if "anki_cards" not in st.session_state:
    st.session_state.anki_cards = 250

if "anki_minutes" not in st.session_state:
    st.session_state.anki_minutes = round(
        st.session_state.anki_cards
        * SECONDS_PER_CARD
        / 60
    )


# =====================================================
# CALLBACKS
# =====================================================

def cards_changed():

    st.session_state.anki_minutes = round(
        st.session_state.anki_cards
        * SECONDS_PER_CARD
        / 60
    )


def minutes_changed():

    cards = round(
        st.session_state.anki_minutes
        * 60
        / SECONDS_PER_CARD
    )

    cards = max(
        0,
        min(MAX_CARDS, cards),
    )

    cards = round(cards / 10) * 10

    st.session_state.anki_cards = cards
    # =====================================================
# SETTINGS
# =====================================================

left, middle, right = st.columns(3)

with left:

    selected_module = st.selectbox(
        "Current Module / Placement",
        module_names,
        key="selected_module",
    )

with middle:

    hours = st.slider(
        "Study Hours Available",
        min_value=1,
        max_value=8,
        key="study_hours",
    )

with right:

    st.subheader("🧠 Daily Anki")

    st.slider(
        "Cards",
        min_value=0,
        max_value=MAX_CARDS,
        step=10,
        key="anki_cards",
        on_change=cards_changed,
    )

    st.number_input(
        "Estimated Time (minutes)",
        min_value=0,
        max_value=60,
        step=1,
        key="anki_minutes",
        on_change=minutes_changed,
    )

    st.success(
        f"🧠 {st.session_state.anki_cards} cards • "
        f"⏱️ ≈ {st.session_state.anki_minutes} minutes"
    )


# =====================================================
# GENERATE / LOAD TODAY'S PLAN
# =====================================================

if st.button("🔄 Generate New Plan"):

    new_plan = generate_plan(
        selected_module,
        hours,
        st.session_state.anki_minutes,
    )

    save_today_plan(
        prepare_plan(new_plan["tasks"])
    )

today_plan = get_today_plan()
# =====================================================
# SUMMARY
# =====================================================

st.divider()

total_minutes = sum(
    task["duration"]
    for task in today_plan
)

completed = sum(
    1
    for task in today_plan
    if task["completed"]
)

c1, c2, c3 = st.columns(3)

with c1:

    st.metric(
        "🧠 Anki",
        f"{st.session_state.anki_cards} cards",
    )

    st.caption(
        f"≈ {st.session_state.anki_minutes} mins"
    )

with c2:

    st.metric(
        "📚 Curriculum",
        f"{total_minutes} mins",
    )

with c3:

    st.metric(
        "⏱ Total",
        f"{total_minutes + st.session_state.anki_minutes} mins",
    )

st.divider()


# =====================================================
# ANKI
# =====================================================

st.header("🧠 Daily Anki")

st.checkbox(
    f"Complete {st.session_state.anki_cards} cards",
    key="anki_today",
)

st.info(
    f"Today's Anki target is "
    f"{st.session_state.anki_cards} cards "
    f"(≈ {st.session_state.anki_minutes} minutes)."
)

st.divider()


# =====================================================
# TODAY'S STUDY
# =====================================================

st.header("📚 Today's Study")

if not today_plan:

    st.info(
        "Press 'Generate New Plan' to create today's study schedule."
    )

else:

    for index, task in enumerate(today_plan, start=1):

        checked = task["completed"]

        new_value = st.checkbox(
            f"{index}. {task['task']}",
            value=checked,
            key=f"task_{task['curriculum_id']}",
        )

        if new_value != checked:

            set_today_completed(
                task["curriculum_id"],
                new_value,
            )

            set_completed(
                task["curriculum_id"],
                new_value,
            )

            st.rerun()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.caption(
                f"📖 {task['learning_type']}"
            )

        with col2:
            st.caption(
                f"📂 {task['topic'] or 'General'}"
            )

        with col3:
            st.caption(
                f"⏱ {task['duration']} min"
            )

        st.divider()
        # =====================================================
# PROGRESS SUMMARY
# =====================================================

if today_plan:

    completed = sum(
        1
        for task in today_plan
        if task["completed"]
    )

    total = len(today_plan)

    progress = (
        completed / total
        if total > 0
        else 0
    )

    st.progress(progress)

    st.caption(
        f"Completed {completed} of {total} study tasks."
    )

    remaining = total - completed

    st.info(
        f"Remaining tasks: {remaining}"
    )

    if completed == total:

        st.balloons()

        st.success(
            "🎉 Great work! You've completed today's study plan."
        )