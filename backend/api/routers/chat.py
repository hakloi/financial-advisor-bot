from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from backend.api.schemas.schemas import ChatRequest, MessageResponse
from backend.auth.database import save_message, load_messages
from backend.auth.jwt import get_current_user
from typing import List

router = APIRouter()


@router.post("/send")
def send_message(body: ChatRequest, current_user=Depends(get_current_user)):
    save_message(current_user["id"], "user", body.message)

    reply = f"Echo: {body.message}"
    save_message(current_user["id"], "assistant", reply)

    def stream():
        for char in reply:
            yield char

    return StreamingResponse(stream(), media_type="text/plain")


@router.get("/history", response_model=List[MessageResponse])
def get_history(current_user=Depends(get_current_user)):
    return load_messages(current_user["id"])
