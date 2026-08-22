from fastapi import APIRouter, HTTPException, status # Web framework for building API, it also shows the status of client's request
from backend.api.schemas.schemas import RegisterRequest, LoginRequest, TokenResponse # Pydantic models for request and response validation
from backend.auth.database import get_user_by_username, get_user_by_email, create_user # Database functions for user management
from backend.auth.hash import hash_password, verify_password # Functions for hashing and verifying passwords
from backend.auth.jwt import create_access_token # Function for creating JWT access tokens

router = APIRouter() # class used to group related API routes together


# Route for user registration, which creates a new user in the database if the username and email are unique
@router.post("/register", status_code=status.HTTP_201_CREATED) # standard HTTP 201 Created success response
def register(body: RegisterRequest):
    if get_user_by_username(body.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    if get_user_by_email(body.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash the password and create the user in the database
    create_user(body.username, body.email, hash_password(body.password))
    return {"detail": "Account created"}


# Route for user login, which verifies the provided credentials and returns a JWT access token if successful
@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest):
    user = get_user_by_username(body.username)
    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create a JWT access token for the authenticated user
    token = create_access_token(user["id"], user["username"])
    return {"access_token": token}
