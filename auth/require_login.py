import streamlit as st

from auth.auth import logout


def require_login():

    if "user" not in st.session_state:

        st.switch_page("app.py")

        st.stop()

    st.sidebar.success(

        f"Logged in as\n\n{st.session_state.user.email}"

    )

    if st.sidebar.button("🚪 Logout"):

        logout()

        del st.session_state.user

        st.switch_page("app.py")