import streamlit as st
from collections import defaultdict

from auth.require_login import require_login

from services.progress_service import (
    get_completed_ids,
    set_completed,
)

from services.supabase_client import supabase


require_login()


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
# LOAD USER PROGRESS
# =====================================================

completed_ids = set(get_completed_ids())


# =====================================================
# SIDEBAR FILTERS
# =====================================================

st.sidebar.header("Filters")


module_response = (
    supabase
    .table("curriculum")
    .select("module")
    .execute()
)


modules = sorted(
    {
        row["module"]
        for row in module_response.data
    }
)


module_names = ["All"] + modules


if "selected_module" not in st.session_state:
    st.session_state.selected_module = "All"


selected_module = st.sidebar.selectbox(
    "Module",
    module_names,
    index=module_names.index(
        st.session_state.selected_module
    )
)


st.session_state.selected_module = selected_module


search = st.sidebar.text_input(
    "🔍 Search",
    placeholder="Search learning activities..."
)


# =====================================================
# LOAD CURRICULUM
# =====================================================

query = (
    supabase
    .table("curriculum")
    .select("*")
)


if selected_module != "All":

    query = query.eq(
        "module",
        selected_module
    )


response = (
    query
    .order("module")
    .execute()
)


rows = response.data


# =====================================================
# FILTER SEARCH
# =====================================================

filtered_rows = []


for row in rows:

    if search:

        if search.lower() not in row["task"].lower():

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

    curriculum[
        row["module"]
    ][
        row["learning_type"]
    ][
        row.get("topic") or ""
    ].append({

        "id": row["id"],

        "task": row["task"],

        "completed": row["id"] in completed_ids

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
# DISPLAY
# =====================================================

for module, learning_types in curriculum.items():


    module_total = 0

    module_done = 0


    for topics in learning_types.values():

        for tasks in topics.values():

            module_total += len(tasks)

            module_done += sum(
                task["completed"]
                for task in tasks
            )


    progress = (
        module_done / module_total
        if module_total
        else 0
    )


    with st.expander(
        f"📚 {module} ({module_done}/{module_total})"
    ):


        st.progress(progress)


        for learning_type, topics in learning_types.items():


            icon = ICONS.get(
                learning_type,
                "📂"
            )


            st.markdown(
                f"## {icon} {learning_type}"
            )


            for topic, tasks in topics.items():


                if topic:


                    with st.expander(
                        f"📂 {topic}"
                    ):


                        for task in tasks:


                            checked = st.checkbox(

                                task["task"],

                                value=task["completed"],

                                key=f"task_{task['id']}"

                            )


                            if checked != task["completed"]:

                                set_completed(
                                    task["id"],
                                    checked
                                )

                                st.rerun()



                else:


                    for task in tasks:


                        checked = st.checkbox(

                            task["task"],

                            value=task["completed"],

                            key=f"task_{task['id']}"

                        )


                        if checked != task["completed"]:

                            set_completed(
                                task["id"],
                                checked
                            )

                            st.rerun()


            st.divider()



# =====================================================
# SUMMARY
# =====================================================

st.sidebar.divider()


total = len(filtered_rows)


done = sum(
    1
    for row in filtered_rows
    if row["id"] in completed_ids
)


percentage = (
    int(done / total * 100)
    if total
    else 0
)


st.sidebar.subheader(
    "Overall Progress"
)


st.sidebar.progress(
    percentage / 100
)


st.sidebar.metric(
    "Completed",
    f"{done}/{total}"
)


st.sidebar.metric(
    "Progress",
    f"{percentage}%"
)


st.divider()


st.caption(
    "🩺 MedTrack • Curriculum Tracker"
)