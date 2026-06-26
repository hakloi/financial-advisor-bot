import streamlit as st
from services.language import load_language

from core.state import init_state
from auth.database import init_db
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

if st.session_state.get("authenticated"):
    page = st.sidebar.radio(t["navigation"], [t["chat"], t["profile"]["profile_title"], t["settings"]["settings_title"]])

    if page == t["profile"]["profile_title"]:
        show_profile(t)
    elif page == t["settings"]["settings_title"]:
        show_settings(t)
    elif page == t["chat"]:
        show_chat(t)