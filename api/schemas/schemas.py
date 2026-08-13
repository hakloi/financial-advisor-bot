from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ProfileUpdate(BaseModel):
    age: Optional[int] = None
    current_savings: Optional[float] = None
    currency: Optional[str] = None
    risk_level: Optional[str] = None
    investment_horizon: Optional[str] = None


class AccountUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = None


class MessageResponse(BaseModel):
    role: str
    content: str
    created_at: datetime


class ChatRequest(BaseModel):
    message: str
    lang: str = "English"
