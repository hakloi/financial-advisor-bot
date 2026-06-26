import streamlit as st

from core.router import route

def show_chat(t):
    st.title(t["chat"])

    


    # -----------------------
    # CHAT HISTORY
    # -----------------------
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])


    # -----------------------
    # INPUT (safe logic)
    # -----------------------
    user_input = st.chat_input(t["chat_placeholder"])


    # -----------------------
    # PROCESS INPUT
    # -----------------------
    if user_input:

        # save user message
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        # route request
        result = route(user_input, st.session_state.lang)
        response = result["response"]

        # save bot message
        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })

        # display bot message
        with st.chat_message("assistant"):
            st.write(response)