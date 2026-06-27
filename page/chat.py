import streamlit as st
from core.router import route


def show_chat(t):
    st.title(t["title"])

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_input = st.chat_input(t["chat_placeholder"])

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            response = st.write_stream(route(user_input, st.session_state.lang))

        st.session_state.messages.append({"role": "assistant", "content": response})
