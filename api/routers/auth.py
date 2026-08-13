from fastapi import APIRouter, HTTPException, status
from api.schemas.schemas import RegisterRequest, LoginRequest, TokenResponse
from auth.database import get_user_by_username, get_user_by_email, create_user
from auth.hash import hash_password, verify_password
from auth.jwt import create_access_token

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest):
    if get_user_by_username(body.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    if get_user_by_email(body.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    create_user(body.username, body.email, hash_password(body.password))
    return {"detail": "Account created"}


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest):
    user = get_user_by_username(body.username)
    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(user["id"], user["username"])
    return {"access_token": token}
