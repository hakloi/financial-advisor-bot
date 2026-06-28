import streamlit as st
from services.language import load_language
from core.state import init_state
from auth.database import init_db, get_user_by_username, get_avatar
from auth.login import show_auth
from page.profile import show_profile
from page.settings import show_settings
from page.chat import show_chat

init_db()
init_state()

st.sidebar.selectbox(
    "Language / Язык",
    ["Русский", "English"],
    key="lang"
)

t = load_language(st.session_state.lang)

if not st.session_state.get("authenticated"):
    show_auth(t)
    st.stop()

# Load messages after authentication
if st.session_state.get("authenticated") and "messages" not in st.session_state:
    from auth.database import load_messages
    user = get_user_by_username(st.session_state.username)
    st.session_state.messages = load_messages(user["id"]) if user else []

if st.session_state.get("authenticated"):
    user = get_user_by_username(st.session_state.username)
    avatar_bytes = get_avatar(user["id"]) if user else None

    page = st.sidebar.radio(t["navigation"], [t["chat"], t["profile"]["profile_title"], t["settings"]["settings_title"]])

    st.sidebar.divider()
    if st.sidebar.button(t["logout"], use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    if page == t["profile"]["profile_title"]:
        show_profile(t)
    elif page == t["settings"]["settings_title"]:
        show_settings(t)
    elif page == t["chat"]:
        show_chat(t)