from backend.api.routers import auth, chat, users  # Import APIRouters
from fastapi import FastAPI #  web framework for building APIs with Python
from fastapi.middleware.cors import CORSMiddleware # a component of middleware to secure connection between frontend and backend
from backend.auth.database import init_db # Import of database initialization 
from backend.finance.market_data_db import init_market_data_table # Initialization of historical market data table
from backend.finance.securities import init_securities_table  # Initialization of securities (shares) table

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

# Initialize database and tables (securities, market data)
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
