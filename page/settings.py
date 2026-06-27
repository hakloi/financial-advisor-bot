import streamlit as st
from auth.database import get_user_by_username, update_user
from auth.hash import hash_password, verify_password


def show_settings(t):
    st.title(t["settings"]["settings_title"])

    user = get_user_by_username(st.session_state.username)
    if not user:
        st.error(t["errors"]["user_not_found"])
        return

    with st.form("settings_form"):
        new_username = st.text_input(t["profile"]["username_label"], value=user["username"])
        new_email = st.text_input(t["profile"]["email_label"], value=user["email"])

        st.divider()

        current_password = st.text_input(t["settings"]["current_password_label"], type="password")
        new_password = st.text_input(t["settings"]["new_password_label"], type="password")

        submitted = st.form_submit_button(t["buttons"]["save_changes"])

    if submitted:
        username_changed = new_username != user["username"]
        email_changed = new_email != user["email"]
        password_changed = bool(new_password)

        if password_changed:
            if not current_password:
                st.error(t["errors"]["no_current_password"])
                return
            if not verify_password(current_password, user["password_hash"]):
                st.error(t["errors"]["incorrect_password"])
                return

        kwargs = {}
        if username_changed:
            kwargs["username"] = new_username
        if email_changed:
            kwargs["email"] = new_email
        if password_changed:
            kwargs["password_hash"] = hash_password(new_password)

        if not kwargs:
            st.info(t["errors"]["no_changes"])
            return

        try:
            update_user(user["id"], **kwargs)
            if username_changed:
                st.session_state.username = new_username
            st.success(t["errors"]["saved"])
            # st.rerun()
        except ValueError as e:
            st.error(str(e))


