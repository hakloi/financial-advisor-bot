import streamlit as st
from auth.database import get_user_by_username, load_messages


def init_state():
    if "lang" not in st.session_state:
        st.session_state.lang = "Русский"

    if "context" not in st.session_state:
        st.session_state.context = {}

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "messages" not in st.session_state:
        user = get_user_by_username(st.session_state.get("username"))
        if user:
            st.session_state.messages = load_messages(user["id"])
        else:
            st.session_state.messages = []
