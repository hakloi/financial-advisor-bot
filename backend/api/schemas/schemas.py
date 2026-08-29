from pydantic import BaseModel, EmailStr, Field # Library used for data validation and settings management
from typing import Optional # Library used for type hinting and optional values
from datetime import date, datetime # Library used for working with dates and times
from enum import Enum # Library used for creating enumerations


# Enum class for supported languages
class Language(str, Enum):
    EN = "en"
    RU = "ru"


# Class representing a user registration request
class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


# Class representing a user login request
class LoginRequest(BaseModel):
    username: str
    password: str


# Class for the response returned after successful authentication, containing the JWT access token and its type
class TokenResponse(BaseModel):
    # JWT access token returned after successful authentication
    access_token: str
    
    # Type of authentication token
    token_type: str = "bearer"


# Class updating user profile information 
class ProfileUpdate(BaseModel):
    age: Optional[int] = None
    current_savings: Optional[float] = None
    currency: Optional[str] = None
    risk_level: Optional[str] = None
    investment_horizon: Optional[str] = None


# Class updating user account information (email, username, password)
class AccountUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = None


class TransactionCreate(BaseModel):
    entry_date: date
    kind: str
    amount: float
    currency: str = Field(default="RUB", min_length=3, max_length=3)
    category: Optional[str] = Field(default=None, max_length=50)
    description: Optional[str] = Field(default=None, max_length=200)


class TransactionResponse(BaseModel):
    id: int
    entry_date: date
    kind: str
    amount: float
    currency: str
    category: Optional[str] = None
    description: Optional[str] = None


# Class representing a message response from the chatbot, including the role of the sender, the content of the message, and the timestamp of when it was created
class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime


# Class representing a chat request sent to the chatbot, including the user's message and the language used for the conversation
class ChatRequest(BaseModel):
    # User's message sent to the chatbot
    message: str

    # Language used for the conversation
    lang: Language = Language.EN
