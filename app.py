import streamlit as st
from services.language import load_language
from core.router import route
from core.state import init_state
from auth.database import init_db
from auth.login import show_auth

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


st.title(t["title"])


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