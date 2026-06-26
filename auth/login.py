import streamlit as st
from auth.database import get_user_by_username, create_user
from auth.hash import hash_password, verify_password


# Shows the authentication interface with login and registration tabs
def show_auth(t):
    tab_login, tab_register = st.tabs([t["auth"]["login_tab"], t["auth"]["register_tab"]])

    with tab_login:
        _login_form(t)

    with tab_register:
        _register_form(t)


def _login_form(t):
    with st.form("login_form"):
        username = st.text_input(t["auth"]["username"])
        password = st.text_input((t["auth"]["password"]), type="password")
        submitted = st.form_submit_button(t["auth"]["login_button"])

    if submitted:
        user = get_user_by_username(username)
        if user and verify_password(password, user["password_hash"]):
            st.session_state.authenticated = True
            st.session_state.username = user["username"]
            st.rerun()
        else:
            st.error(t["auth"]["login_error"])


def _register_form(t):
    with st.form("register_form"):
        username = st.text_input(t["auth"]["username"])
        email = st.text_input(t["auth"]["email"])
        password = st.text_input(t["auth"]["password"], type="password")
        submitted = st.form_submit_button(t["auth"]["register_button"])

    if submitted:
        if get_user_by_username(username):
            st.error(t["auth"]["user_exists"])
        elif get_user_by_username(email):
            st.error(t["auth"]["email_exists"])
        else:
            created = create_user(username, email, hash_password(password))

            if created:
                st.success(t["auth"]["success_register"])
            else:
                st.error(t["auth"]["email_exists"])
