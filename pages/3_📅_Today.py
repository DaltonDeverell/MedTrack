import streamlit as st
import sqlite3

from planner.planner import generate_plan

# =====================================================
# PAGE
# =====================================================

st.set_page_config(
    page_title="Today",
    page_icon="📅",
    layout="wide"
)

st.title("📅 Today's Study")

st.write("Your personalised study plan for today.")

# =====================================================
# DATABASE
# =====================================================

conn = sqlite3.connect("database/medtrack.db")
conn.row_factory = sqlite3.Row

modules = conn.execute("""
SELECT DISTINCT module
FROM curriculum
ORDER BY module
""").fetchall()

module_names = ["All"] + [m["module"] for m in modules]

# =====================================================
# SETTINGS
# =====================================================

left, right = st.columns(2)

with left:

    selected_module = st.selectbox(
        "Current Module / Placement",
        module_names
    )

with right:

    hours = st.slider(
        "Study Hours Available",
        1,
        8,
        3
    )

# =====================================================
# GENERATE PLAN
# =====================================================

plan = generate_plan(
    selected_module,
    hours
)

# =====================================================
# SUMMARY
# =====================================================

st.divider()

c1, c2, c3 = st.columns(3)

c1.metric("🧠 Anki", f"{plan['anki_minutes']} min")
c2.metric("📚 Curriculum", f"{plan['curriculum_minutes']} min")
c3.metric("⏱ Total", f"{plan['total_minutes']} min")

st.divider()

# =====================================================
# ANKI
# =====================================================

st.header("🧠 Daily Anki")

st.checkbox(
    f"Complete Anki ({plan['anki_minutes']} min)",
    key="anki_today"
)

st.info(
    f"Today's Anki target: {plan['anki_minutes']} minutes"
)

st.divider()

# =====================================================
# TODAY'S STUDY
# =====================================================

st.header("📚 Today's Study")

if not plan["tasks"]:

    st.success("🎉 Everything has been completed!")

else:

    completed = 0

    for i, task in enumerate(plan["tasks"], start=1):

        current_value = bool(
            conn.execute(
                """
                SELECT completed
                FROM curriculum
                WHERE id=?
                """,
                (task["id"],)
            ).fetchone()[0]
        )

        checked = st.checkbox(
            f"{i}. {task['task']}",
            value=current_value,
            key=f"today_{task['id']}"
        )

        if checked != current_value:

            conn.execute(
                """
                UPDATE curriculum
                SET completed=?
                WHERE id=?
                """,
                (
                    int(checked),
                    task["id"]
                )
            )

            conn.commit()

            st.rerun()

        if checked:
            completed += 1

        a, b, c = st.columns(3)

        with a:
            st.caption(f"📖 {task['learning_type']}")

        with b:
            st.caption(
                f"📂 {task['topic']}"
                if task["topic"]
                else "📂 General"
            )

        with c:
            st.caption(f"⏱ {task['duration']} min")

        st.divider()

    st.progress(completed / len(plan["tasks"]))

    st.caption(
        f"Completed {completed} of {len(plan['tasks'])} study tasks."
    )

conn.close()