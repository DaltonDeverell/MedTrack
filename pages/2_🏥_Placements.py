import streamlit as st
from auth.require_login import require_login

require_login()
import pandas as pd

st.set_page_config(page_title="Placements", layout="wide")

st.title("🏥 Placements")

rotations = pd.DataFrame({

    "Rotation": [
        "Mental Health",
        "Medicine 1",
        "Medicine 2",
        "Surgery 1",
        "Surgery 2",
        "O&G",
        "Paediatrics"
    ],

    "Start Date": [
        "",
        "",
        "",
        "",
        "",
        "",
        ""
    ],

    "End Date": [
        "",
        "",
        "",
        "",
        "",
        "",
        ""
    ]

})

edited = st.data_editor(
    rotations,
    use_container_width=True,
    hide_index=True
)

st.success("Rotation editor coming soon.")