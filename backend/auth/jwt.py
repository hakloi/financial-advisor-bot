import os
import PyJWT as jwt
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status # FastAPI classes for handling dependencies, HTTP exceptions, and status codes
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials # FastAPI classes for implementing HTTP Bearer authentication and handling authorization credentials

SECRET_KEY = os.getenv("SECRET_KEY", "change_me_in_production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

# Define a security scheme for HTTP Bearer authentication, which will be used to protect routes that require authentication
bearer_scheme = HTTPBearer()


# Function to create a JWT access token for a user, including the user's ID and username in the token's payload, and setting an expiration time for the token
def create_access_token(user_id: int, username: str) -> str:
    payload = {
        "sub": str(user_id),
        "username": username,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# Function to retrieve the current authenticated user based on the provided JWT access token, decoding the token and extracting the user's ID and username from the payload. If the token is expired or invalid, an HTTP 401 Unauthorized exception is raised.
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return {"id": int(payload["sub"]), "username": payload["username"]}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
