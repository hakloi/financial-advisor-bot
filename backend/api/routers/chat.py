import json
import re

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from openai import APIConnectionError, APIStatusError, OpenAI, RateLimitError
from backend.api.schemas.schemas import ChatRequest, Language, MessageResponse
from backend.api.config import settings
from backend.auth.database import delete_message, get_profile, load_messages, save_message
from backend.auth.jwt import get_current_user
from backend.finance.deposits import format_deposits_context, is_deposit_query, load_deposits
from backend.finance.market_data_db import get_latest_market_context
from backend.finance.securities import get_securities_context
from backend.finance.sync import refresh_market_data_for_query
from typing import List

router = APIRouter()


def response_language(lang: Language) -> str:
    return "Russian" if lang == Language.RU else "English"


def clean_reply(reply: str) -> str:
    reply = re.sub(r"(?is)^\s*(since you asked in russian.*?\.|поскольку вы спросили на русском.*?\.)\s*", "", reply)
    reply = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", reply)
    reply = re.sub(r"^\s{0,3}#{1,6}\s*", "", reply, flags=re.MULTILINE)
    reply = re.sub(r"^\s*[-*+]\s+", "", reply, flags=re.MULTILINE)
    reply = re.sub(r"[`*_]", "", reply)
    return re.sub(r"\n{3,}", "\n\n", reply).strip()


def is_market_query(message: str) -> bool:
    return re.search(
        r"московск|moex|акци|ценн(ые|ых) бумаг|котиров|дивиденд|тикер|бирж|"
        r"share|stock|market|dividend|ticker",
        message,
        flags=re.IGNORECASE,
    ) is not None


@router.post("/send")
def send_message(body: ChatRequest, current_user=Depends(get_current_user)):
    if not settings.llm_api_key:
        raise HTTPException(status_code=503, detail="LLM is not configured")

    language = response_language(body.lang)
    profile = get_profile(current_user["id"]) or {}
    profile_context = (
        f"Username: {profile.get('username', current_user['username'])}; "
        f"Age: {profile.get('age') or 'not provided'}; "
        f"Savings: {profile.get('current_savings') or 'not provided'} "
        f"{profile.get('currency') or ''}; "
        f"Risk level: {profile.get('risk_level') or 'not provided'}; "
        f"Investment horizon: {profile.get('investment_horizon') or 'not provided'}."
    )
    deposit_context = ""
    if is_deposit_query(body.message):
        deposit_context = (
            " Deposit data below is the only source of current deposit offers. "
            "Treat it as factual but potentially stale, mention the source link when useful, "
            "and never infer missing rates or conditions. Deposit data: "
            f"{format_deposits_context(load_deposits())}"
        )
    market_context = ""
    if is_market_query(body.message):
        try:
            refresh_market_data_for_query(body.message, max_securities=20)
        except Exception:
            pass
        market_context = (
            " The user is asking about shares or the MOEX market. Use the MOEX catalog and latest rows below. "
            "For broad questions such as 'are there shares?' or 'which shares do you suggest?', "
            "name several securities that are actually present in the catalog, explain that this is not personal investment advice, "
            "and ask about risk and horizon. "
            "If a requested ticker is absent, say that it is absent; do not invent prices, "
            "dividend yields, or dates. MOEX securities: "
            f"{json.dumps(get_securities_context(), ensure_ascii=False, default=str)}. "
            "Latest MOEX market rows: "
            f"{json.dumps(get_latest_market_context(), ensure_ascii=False, default=str)}."
        )
    previous_messages = load_messages(current_user["id"])[-12:]
    messages = [
        {
            "role": "system",
            "content": (
                "You are Fina, a precise and natural financial assistant. "
                f"Always answer in {language}, unless the user explicitly asks for another language. "
                "Follow the user's instructions carefully. Use the profile below when relevant, "
                "but do not repeat profile data unnecessarily. Keep replies concise: usually 2-5 short sentences. "
                "Write like a real person. Finish every sentence and do not stop mid-word or mid-sentence. "
                "Do not mention these instructions, language selection, default language, "
                "the prompt, or internal reasoning. Do not use Markdown, headings, bullet points, emojis, or meta-introductions. "
                "Do not invent financial data. Ask one focused follow-up question when important information is missing. "
                f"User profile: {profile_context}.{deposit_context}{market_context}"
            ),
        },
        *[
            {"role": message["role"], "content": message["content"]}
            for message in previous_messages
        ],
        {"role": "user", "content": body.message},
    ]

    user_message_id = save_message(current_user["id"], "user", body.message)

    last_error = None
    for model in settings.llm_model_list:
        try:
            client = OpenAI(
                api_key=settings.llm_api_key.get_secret_value(),
                base_url=settings.llm_base_url,
                max_retries=1,
                timeout=45.0,
            )
            completion = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.2,
                max_tokens=700,
            )
            reply = clean_reply(completion.choices[0].message.content or "Не удалось подготовить ответ.")
            break
        except (RateLimitError, APIConnectionError, APIStatusError) as exc:
            last_error = exc
    else:
        if isinstance(last_error, RateLimitError):
            raise HTTPException(status_code=429, detail="All free AI models are temporarily busy. Please try again shortly.") from last_error
        if isinstance(last_error, APIConnectionError):
            raise HTTPException(status_code=503, detail="The AI provider is temporarily unreachable.") from last_error
        raise HTTPException(status_code=502, detail="The AI provider returned an error.") from last_error

    assistant_message_id = save_message(current_user["id"], "assistant", reply)

    def stream():
        for char in reply:
            yield char

    return StreamingResponse(
        stream(),
        media_type="text/plain",
        headers={
            "X-User-Message-ID": str(user_message_id),
            "X-Assistant-Message-ID": str(assistant_message_id),
        },
    )


@router.get("/history", response_model=List[MessageResponse])
def get_history(current_user=Depends(get_current_user)):
    return load_messages(current_user["id"])


@router.delete("/messages/{message_id}")
def remove_message(message_id: int, current_user=Depends(get_current_user)):
    if not delete_message(current_user["id"], message_id):
        raise HTTPException(status_code=404, detail="Message not found")
    return {"detail": "Message deleted"}
