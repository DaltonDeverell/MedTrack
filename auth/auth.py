import streamlit as st

from services.supabase_client import supabase

# =====================================================
# SIGN UP
# =====================================================

def signup(email, password):

    try:

        response = supabase.auth.sign_up(
            {
                "email": email,
                "password": password
            }
        )

        if response.user is None:

            return None

        return response.user

    except Exception as e:

        st.error(str(e))

        return None


# =====================================================
# LOGIN
# =====================================================

def login(email, password):

    try:

        response = supabase.auth.sign_in_with_password(
            {
                "email": email,
                "password": password
            }
        )

        if response.user is None:

            return None

        st.session_state["user"] = response.user

        return response.user

    except Exception as e:

        st.error(str(e))

        return None


# =====================================================
# LOGOUT
# =====================================================

def logout():

    try:

        supabase.auth.sign_out()

    except:
        pass

    st.session_state.pop("user", None)


# =====================================================
# CURRENT USER
# =====================================================

def current_user():

    return st.session_state.get("user")