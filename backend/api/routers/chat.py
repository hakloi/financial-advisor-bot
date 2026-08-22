from fastapi import APIRouter, Depends # Web framework for building API and dependency injection system 
from fastapi.responses import StreamingResponse # Class for streaming responses, allowing the server to send data in chunks
from backend.api.schemas.schemas import ChatRequest, MessageResponse # Pydantic models for request and response validation
from backend.auth.database import get_profile, get_user_by_username, save_message, load_messages # Database functions for user management and message handling
from backend.services.llm import ask_llm_stream
from backend.auth.jwt import get_current_user # Dependency function to get the current authenticated user
from typing import List # Library used for type hinting and working with lists

router = APIRouter() # Class used to group related API routes together


# Inner function to build the prompt for the language model based on user input, profile data, and conversation history
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
            - You can strongly recommend deposits, savings accounts, because it is a good way to save money and earn interest
            - Do not be biased or promote specific banks or financial institutions
            - Help the user understand financial concepts and options
            - Be the teacher for the user, help them learn about finance and make informed decisions
            - Help to change bahaviour which is not good for financial health, like overspending, not saving, not investing, etc.
            - Reply ONLY as the assistant. Do not write "User:" or simulate user messages.{clarify}
            {history_section}
            User: {message}
            Assistant:"""


# Route for sending a message to the chatbot, which processes the user's input, generates a response using a language model, and streams the response back to the client
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


# Route for retrieving the chat history for the current user, which returns a list of messages exchanged with the chatbot
@router.get("/history", response_model=List[MessageResponse])
def get_history(current_user=Depends(get_current_user)):
    return load_messages(current_user["id"])
