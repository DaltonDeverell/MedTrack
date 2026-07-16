import streamlit as st

from auth.auth import login, signup

st.title("Login Test")

mode = st.radio(

    "Mode",

    ["Login", "Sign Up"]

)

email = st.text_input("Email")

password = st.text_input(

    "Password",

    type="password"

)

if st.button("Continue"):

    if mode == "Login":

        user = login(email, password)

    else:

        user = signup(email, password)

    st.write(user)