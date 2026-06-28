import streamlit as st
from PIL import Image
import io
from datetime import datetime, date
from core.router import route
from auth.database import get_user_by_username, get_avatar, save_message

BOT_AVATAR = Image.open("static/img/young_man_bot.png")
# Author: https://www.flaticon.com/ru/free-icons/ Good Ware - Flaticon


def _get_user_avatar():
    user = get_user_by_username(st.session_state.username)
    if not user:
        return None
    avatar_bytes = get_avatar(user["id"])
    if avatar_bytes:
        return Image.open(io.BytesIO(avatar_bytes))
    return None


def _format_date(dt):
    today = date.today()
    d = dt.date() if isinstance(dt, datetime) else dt
    if d == today:
        return "Сегодня" if st.session_state.lang == "Русский" else "Today"
    if (today - d).days == 1:
        return "Вчера" if st.session_state.lang == "Русский" else "Yesterday"
    return d.strftime("%d.%m.%Y")


def _format_time(dt):
    if isinstance(dt, datetime):
        return dt.strftime("%H:%M")
    return ""


def show_chat(t):
    st.title(t["title"])

    user_avatar = _get_user_avatar()

    last_date = None
    for msg in st.session_state.messages:
        dt = msg.get("created_at")

        # Date separator
        if dt:
            msg_date = dt.date() if isinstance(dt, datetime) else None
            if msg_date and msg_date != last_date:
                st.markdown(
                    f"<div style='text-align:center; color:gray; font-size:0.8em; margin:8px 0'>{_format_date(dt)}</div>",
                    unsafe_allow_html=True
                )
                last_date = msg_date

        avatar = BOT_AVATAR if msg["role"] == "assistant" else user_avatar
        with st.chat_message(msg["role"], avatar=avatar):
            st.write(msg["content"])
            if dt:
                st.markdown(
                    f"<div style='font-size:0.75em; color:gray; text-align:right'>{_format_time(dt)}</div>",
                    unsafe_allow_html=True
                )

    user_input = st.chat_input(t["chat_placeholder"])

    if user_input:
        user = get_user_by_username(st.session_state.username)

        user_ts = save_message(user["id"], "user", user_input)
        st.session_state.messages.append({"role": "user", "content": user_input, "created_at": user_ts})

        with st.chat_message("user", avatar=user_avatar):
            st.write(user_input)
            st.markdown(
                f"<div style='font-size:0.75em; color:gray; text-align:right'>{_format_time(user_ts)}</div>",
                unsafe_allow_html=True
            )

        with st.chat_message("assistant", avatar=BOT_AVATAR):
            response = st.write_stream(route(user_input, st.session_state.lang))

        bot_ts = save_message(user["id"], "assistant", response)
        st.session_state.messages.append({"role": "assistant", "content": response, "created_at": bot_ts})
