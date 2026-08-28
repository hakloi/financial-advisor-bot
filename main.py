from backend.api.routers import auth, chat
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.auth.database import init_db
from backend.api.routers import users
from backend.finance.market_data_db import init_market_data_table
from backend.finance.securities import init_securities_table

# Create FastAPI app
app = FastAPI(title="Fina - Financial Advisor Chatbot", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()
init_securities_table()
init_market_data_table()

# Include routers 
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])


# Health check endpoint
@app.get("/health")
def health():
    return {"status": "ok"}
