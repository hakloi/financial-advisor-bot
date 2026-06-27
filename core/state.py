import streamlit as st


def init_state():

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "lang" not in st.session_state:
        st.session_state.lang = "Русский"

    if "context" not in st.session_state:
        st.session_state.context = {}

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []