import streamlit as st
from auth.database import get_user_by_username


def show_profile(t):
    st.title(t["profile"]["profile_title"])

    user = get_user_by_username(st.session_state.username)
    if not user:
        st.error("User not found")
        return

    
    
    
