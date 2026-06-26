import streamlit as st


def show_settings(t):
    st.title(t["settings"]["settings_title"])

    # username = st.text_input(t["profile"]["username"])
    # email = st.text_input(t["profile"]["email"])
    # password = st.text_input(t["profile"]["password"], type="password")