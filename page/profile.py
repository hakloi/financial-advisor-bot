import streamlit as st
from auth.database import get_user_by_username, get_profile, update_profile

RISK_KEYS = ["low", "medium", "high"]
HORIZON_KEYS = ["short", "medium", "long"]


def show_profile(t):
    p = t["profile"]
    st.title(p["profile_title"])

    user = get_user_by_username(st.session_state.username)
    if not user:
        st.error(t["errors"]["user_not_found"])
        return

    st.subheader(f"{p['welcome_label']}, {user['username']}!")
    st.divider()

    profile = get_profile(user["id"])

    risk_labels = [p["low"], p["medium"], p["high"]]
    horizon_labels = [p["horizon_short"], p["horizon_medium"], p["horizon_long"]]

    saved_risk = profile["risk_level"] if profile and profile["risk_level"] in RISK_KEYS else "medium"
    saved_horizon = profile["investment_horizon"] if profile and profile["investment_horizon"] in HORIZON_KEYS else "short"

    with st.form("profile_form"):
        age = st.number_input(
            p["age_label"],
            min_value=1, max_value=110,
            value=profile["age"] if profile and profile["age"] else 18
        )
        current_savings = st.number_input(
            p["current_savings"],
            min_value=0.0,
            value=float(profile["current_savings"]) if profile and profile["current_savings"] else 0.0
        )
        currency = st.selectbox(
            p["currency_label"],
            ["RUB", "USD"],
            index=0 if not profile or profile["currency"] == "RUB" else 1
        )
        risk_index = st.selectbox(
            p["risk"],
            risk_labels,
            index=RISK_KEYS.index(saved_risk)
        )
        horizon_index = st.selectbox(
            p["investment_horizon"],
            horizon_labels,
            index=HORIZON_KEYS.index(saved_horizon)
        )

        if st.form_submit_button(t["buttons"]["save_changes"]):
            # Save fixed keys to DB, not translated labels
            risk_key = RISK_KEYS[risk_labels.index(risk_index)]
            horizon_key = HORIZON_KEYS[horizon_labels.index(horizon_index)]
            update_profile(user["id"], age, current_savings, currency, risk_key, horizon_key)
            st.success(t["errors"]["saved"])
            # st.rerun()
