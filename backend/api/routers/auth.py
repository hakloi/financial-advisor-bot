import secrets
import hashlib
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Query, status # Web framework for building API, it also shows the status of client's request
from fastapi.responses import RedirectResponse
from backend.api.schemas.schemas import RegisterRequest, LoginRequest, TokenResponse # Pydantic models for request and response validation
from backend.auth.database import confirm_user_email, get_user_by_username, get_user_by_email, create_user # Database functions for user management
from backend.auth.hash import hash_password, verify_password # Functions for hashing and verifying passwords
from backend.auth.jwt import create_access_token # Function for creating JWT access tokens
from backend.services.celery_app import celery_app
from backend.api.config import settings

router = APIRouter() # class used to group related API routes together


# Route for user registration, which creates a new user in the database if the username and email are unique
@router.post("/register", status_code=status.HTTP_201_CREATED) # standard HTTP 201 Created success response
def register(body: RegisterRequest):
    if get_user_by_username(body.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    if get_user_by_email(body.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash the password and create the user in the database
    confirmation_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(confirmation_token.encode()).hexdigest()
    token_expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
    create_user(
        body.username,
        body.email,
        hash_password(body.password),
        token_hash,
        token_expires_at,
    )
    celery_app.send_task(
        "backend.services.tasks.send_confirmation_email",
        args=[body.email, confirmation_token, body.username],
        retry=True,
        retry_policy={
            "max_retries": 3,
            "interval_start": 0,
            "interval_step": 0.5,
            "interval_max": 2,
        },
    )
    return {"detail": "Account created"}


@router.get("/confirm")
def confirm_email(token: str = Query(..., min_length=1)):
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    if not confirm_user_email(token_hash):
        raise HTTPException(status_code=400, detail="Invalid or expired confirmation link")
    return {"detail": "Email confirmed"}


@router.get("/register_confirm")
def legacy_confirm_email(token: str = Query(..., min_length=1)):
    return RedirectResponse(url=f"{settings.frontend_url}/confirm-email?token={token}")


# Route for user login, which verifies the provided credentials and returns a JWT access token if successful
@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest):
    user = get_user_by_username(body.username)
    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user["email_verified"]:
        raise HTTPException(status_code=403, detail="Please confirm your email first")

    # Create a JWT access token for the authenticated user
    token = create_access_token(user["id"], user["username"])
    return {"access_token": token}
