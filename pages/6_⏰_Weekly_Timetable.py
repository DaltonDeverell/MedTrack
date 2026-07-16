import streamlit as st

from timetable.timetable_service import (
    DAYS,
    BLOCK_TYPES,
    add_block,
    delete_block,
    load_blocks
)

# =====================================================
# PAGE
# =====================================================

st.set_page_config(
    page_title="Weekly Timetable",
    page_icon="🕒",
    layout="wide"
)

st.title("🕒 Weekly Timetable")

st.write(
    """
Build your recurring weekly timetable.

These recurring events are used by MedTrack to schedule
your study around placements, work and personal commitments.
"""
)

st.divider()

# =====================================================
# ADD BLOCK
# =====================================================

st.subheader("➕ Add Weekly Block")

c1, c2, c3 = st.columns(3)

with c1:

    title = st.text_input(
        "Title",
        placeholder="e.g. Mental Health Placement"
    )

    day = st.selectbox(
        "Day",
        DAYS
    )

with c2:

    start = st.time_input(
        "Start Time"
    )

    end = st.time_input(
        "End Time"
    )

with c3:

    block_type = st.selectbox(
        "Block Type",
        list(BLOCK_TYPES.keys())
    )

    st.write("")

    if st.button(
        "💾 Save Block",
        use_container_width=True
    ):

        if title.strip() == "":

            st.warning("Please enter a title.")

        elif end <= start:

            st.warning("End time must be after start time.")

        else:

            add_block(

                day,

                start.strftime("%H:%M"),

                end.strftime("%H:%M"),

                block_type,

                title

            )

            st.success("Block saved.")

            st.rerun()

st.divider()

# =====================================================
# CURRENT TIMETABLE
# =====================================================

st.subheader("📅 Weekly Timetable")

blocks = load_blocks()

if len(blocks) == 0:

    st.info("No recurring events yet.")

else:

    for day in DAYS:

        day_blocks = [

            b

            for b in blocks

            if b["day"] == day

        ]

        with st.expander(
            day,
            expanded=True
        ):

            if len(day_blocks) == 0:

                st.caption("No events")

            else:

                for block in day_blocks:

                    left, middle, right = st.columns([5,2,1])

                    with left:

                        st.markdown(

                            f"**{block['title']}**"

                        )

                        st.caption(

                            f"{block['start_time']} → {block['end_time']}"

                        )

                    with middle:

                        st.markdown(

                            f":{block['block_type']}:"

                        )

                        st.caption(

                            block["block_type"]

                        )

                    with right:

                        if st.button(

                            "🗑",

                            key=f"delete_{block['id']}"

                        ):

                            delete_block(

                                block["id"]

                            )

                            st.rerun()