from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from api.schemas.schemas import ChatRequest, MessageResponse
from auth.database import get_profile, get_user_by_username, save_message, load_messages
from services.llm import ask_llm_stream
from auth.jwt import get_current_user
from typing import List

router = APIRouter()


def _build_prompt(message: str, lang: str, profile: dict, history: list) -> str:
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

    clarify = f"\nIf relevant, politely ask the user to fill in: {', '.join(missing)}." if missing else ""

    history_section = ""
    if history:
        lines = "\n".join(f"{m['role'].capitalize()}: {m['content']}" for m in history[-10:])
        history_section = f"\nConversation so far:\n{lines}\n"

    return f"""You are a personal financial assistant named Fineas.
Language to respond in: {lang}
{profile_section}

Your behavior:
- Use the user's profile data to personalize answers
- Explain financial information clearly
- Do not provide direct financial advice
- Reply ONLY as the assistant. Do not write "User:" or simulate user messages.{clarify}
{history_section}
User: {message}
Assistant:"""


@router.post("/send")
def send_message(body: ChatRequest, current_user=Depends(get_current_user)):
    profile = get_profile(current_user["id"])
    history = load_messages(current_user["id"])

    prompt = _build_prompt(body.message, body.lang, profile, history)

    save_message(current_user["id"], "user", body.message)

    full_response = []

    def stream():
        for chunk in ask_llm_stream(prompt):
            full_response.append(chunk)
            yield chunk
        save_message(current_user["id"], "assistant", "".join(full_response))

    return StreamingResponse(stream(), media_type="text/plain")


@router.get("/history", response_model=List[MessageResponse])
def get_history(current_user=Depends(get_current_user)):
    return load_messages(current_user["id"])
