import streamlit as st
from services.language import load_language
from core.router import route
from core.state import init_state


init_state()

st.sidebar.selectbox(
    "Language / Язык",
    ["Русский", "English"],
    key="lang"
)

t = load_language(st.session_state.lang)


st.title(t["title"])




# -----------------------
# CHAT HISTORY
# -----------------------
st.write(t["quick_choices"])

col1, col2 = st.columns(2)

quick_message = None  # ✔ ВСЕГДА заранее

with col1:
    if st.button(t["stocks"]):
        quick_message = t["stocks"]

with col2:
    if st.button(t["deposits"]):
        quick_message = t["deposits"]


# -----------------------
# CHAT HISTORY
# -----------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])


# -----------------------
# INPUT (safe logic)
# -----------------------
if quick_message is not None:
    user_input = quick_message
else:
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