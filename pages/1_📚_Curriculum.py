import streamlit as st
import sqlite3
from collections import defaultdict

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Curriculum",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Curriculum")

# =====================================================
# DATABASE
# =====================================================

conn = sqlite3.connect("database/medtrack.db")
conn.row_factory = sqlite3.Row

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.header("Filters")

modules = conn.execute("""
SELECT DISTINCT module
FROM curriculum
ORDER BY module
""").fetchall()

module_names = ["All"] + [m["module"] for m in modules]

selected_module = st.sidebar.selectbox(
    "Module",
    module_names
)

search = st.sidebar.text_input(
    "🔍 Search",
    placeholder="Search learning activities..."
)

show_completed = st.sidebar.checkbox(
    "Show completed",
    value=True
)

st.sidebar.divider()

# =====================================================
# LOAD CURRICULUM
# =====================================================

if selected_module == "All":

    rows = conn.execute("""
    SELECT *
    FROM curriculum
    ORDER BY
        module,
        learning_type,
        topic,
        task
    """).fetchall()

else:

    rows = conn.execute("""
    SELECT *
    FROM curriculum
    WHERE module=?
    ORDER BY
        learning_type,
        topic,
        task
    """,(selected_module,)).fetchall()

# =====================================================
# FILTERS
# =====================================================

filtered_rows = []

for row in rows:

    if search:

        if search.lower() not in row["task"].lower():

            continue

    if not show_completed:

        if row["completed"]:

            continue

    filtered_rows.append(row)

# =====================================================
# BUILD HIERARCHY
# =====================================================

curriculum = defaultdict(
    lambda: defaultdict(
        lambda: defaultdict(list)
    )
)

for row in filtered_rows:

    module = row["module"]

    learning_type = row["learning_type"]

    topic = row["topic"]

    if topic is None:
        topic = ""

    curriculum[module][learning_type][topic].append({

        "id": row["id"],

        "task": row["task"],

        "completed": bool(row["completed"])

    })

# =====================================================
# ICONS
# =====================================================

ICONS = {

    "Lectures":"📖",

    "Tutorials":"👥",

    "Clinical Skills":"🩺",

    "Clinical Pharmacology":"💊",

    "CBL Cases":"🧠",

    "CBL cases":"🧠",

    "SDL":"📚",

    "Practicals":"🧪",

    "Online Modules":"💻",

    "Videos":"🎥"

}

# =====================================================
# DISPLAY MODULES
# =====================================================
# =====================================================
# RENDER MODULES
# =====================================================

for module, learning_types in curriculum.items():

    module_total = 0
    module_done = 0

    for topics in learning_types.values():
        for tasks in topics.values():
            module_total += len(tasks)
            module_done += sum(task["completed"] for task in tasks)

    module_percent = (
        int((module_done / module_total) * 100)
        if module_total else 0
    )

    with st.expander(
        f"📚 {module} ({module_done}/{module_total} • {module_percent}%)",
        expanded=False
    ):

        st.progress(module_percent / 100)

        st.caption(
            f"{module_done} completed • "
            f"{module_total - module_done} remaining"
        )

        st.divider()

        # =============================================
        # LEARNING TYPES
        # =============================================

        for learning_type, topics in learning_types.items():

            learning_total = sum(
                len(tasks)
                for tasks in topics.values()
            )

            learning_done = sum(
                task["completed"]
                for tasks in topics.values()
                for task in tasks
            )

            learning_percent = (
                int((learning_done / learning_total) * 100)
                if learning_total else 0
            )

            icon = ICONS.get(learning_type, "📂")

            st.markdown(
                f"## {icon} {learning_type}"
            )

            st.progress(learning_percent / 100)

            st.caption(
                f"{learning_done}/{learning_total} completed"
            )

            # =========================================
            # TOPICS
            # =========================================

            for topic, tasks in topics.items():

                if topic.strip():

                    with st.expander(
                        f"📂 {topic}",
                        expanded=False
                    ):

                        for task in tasks:

                            checked = st.checkbox(
                                task["task"],
                                value=task["completed"],
                                key=f"task_{task['id']}"
                            )

                            if checked != task["completed"]:

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

                else:

                    for task in tasks:

                        checked = st.checkbox(
                            task["task"],
                            value=task["completed"],
                            key=f"task_{task['id']}"
                        )

                        if checked != task["completed"]:

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

            st.divider()
            # =====================================================
# OVERALL SUMMARY
# =====================================================

st.sidebar.divider()

overall_total = len(filtered_rows)

overall_done = sum(
    1
    for row in filtered_rows
    if row["completed"]
)

overall_percent = (
    int((overall_done / overall_total) * 100)
    if overall_total else 0
)

st.sidebar.subheader("Overall Progress")

st.sidebar.progress(overall_percent / 100)

st.sidebar.metric(
    "Completion",
    f"{overall_done}/{overall_total}",
    f"{overall_percent}%"
)

remaining = overall_total - overall_done

st.sidebar.metric(
    "Remaining",
    remaining
)

# =====================================================
# FOOTER
# =====================================================

st.divider()

st.caption(
    "🩺 MedTrack • Curriculum Tracker"
)

conn.close()