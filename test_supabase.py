import streamlit as st

from auth.auth import login, logout, current_user

st.title("Supabase Test")

user = current_user()

if user:

    st.success(f"Logged in as {user.email}")

    st.write(user)

    if st.button("Logout"):

        logout()

        st.rerun()

else:

    st.warning("Not logged in")

    email = st.text_input("Email")

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):

        logged_in = login(
            email,
            password
        )

        if logged_in:

            st.rerun()