import streamlit as st
from services.llm import ask_llm_stream
from auth.database import get_user_by_username, get_profile


def _build_system_prompt(lang: str) -> str:
    username = st.session_state.get("username")
    user = get_user_by_username(username) if username else None
    profile = get_profile(user["id"]) if user else None

    profile_section = ""
    missing = []

    if profile:
        fields = {
            "Age": profile.get("age"),
            "Current savings": profile.get("current_savings"),
            "Currency": profile.get("currency"),
            "Risk level": profile.get("risk_level"),
            "Investment horizon": profile.get("investment_horizon"),
        }
        filled = {k: v for k, v in fields.items() if v is not None}
        missing = [k for k, v in fields.items() if v is None]

        if filled:
            profile_section = "User profile:\n" + "\n".join(f"- {k}: {v}" for k, v in filled.items())
    else:
        missing = ["age", "current savings", "risk level", "investment horizon"]

    clarify = ""
    if missing:
        clarify = f"\nIf relevant, politely ask the user to fill in: {', '.join(missing)}."

    return f"""You are a personal financial assistant.
Language to respond in: {lang}
{profile_section}

Your behavior:
- Your name is Fineas
- Use the user's profile data to personalize answers
- If profile data is missing, ask the user to fill it in the Profile section
- Explain financial information clearly
- Do not provide direct financial advice
- Reply ONLY as the assistant. Do not write "User:" or simulate user messages.{clarify}"""


def _build_history() -> str:
    history = st.session_state.get("chat_history", [])
    if not history:
        return ""
    lines = "\n".join(f"{m['role'].capitalize()}: {m['content']}" for m in history[-10:])
    return f"\nConversation so far:\n{lines}\n"


def route(message: str, lang: str):
    system = _build_system_prompt(lang)
    history = _build_history()
    prompt = f"{system}{history}\nUser: {message}\nAssistant:"

    # Save to history
    st.session_state.chat_history.append({"role": "user", "content": message})

    full_response = []

    for chunk in ask_llm_stream(prompt):
        full_response.append(chunk)
        yield chunk

    st.session_state.chat_history.append({"role": "assistant", "content": "".join(full_response)})
