from backend.api.routers import auth, chat
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.auth.database import init_db
from backend.api.routers import users

app = FastAPI(title="Financial Advisor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])


@app.get("/health")
def health():
    return {"status": "ok"}
