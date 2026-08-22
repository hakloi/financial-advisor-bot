from fastapi import APIRouter, Depends, HTTPException, UploadFile, File # Libraries for building API routes, handling dependencies, raising HTTP exceptions, and managing file uploads
from PIL import Image # Library for image processing, used to handle avatar images
import io # Library for handling input/output operations, used to manage image data in memory
from backend.api.schemas.schemas import ProfileUpdate, AccountUpdate # Pydantic models for validating and managing user profile and account update requests
from backend.auth.database import get_profile, update_profile, get_avatar, update_avatar, update_user, get_user_by_username # Database functions for retrieving and updating user profile, avatar, and account information
from backend.auth.hash import hash_password, verify_password # Functions for hashing and verifying passwords
from backend.auth.jwt import get_current_user # Dependency function to get the current authenticated user

router = APIRouter() # Class used to group related API routes together


## Route for retrieving the user's profile information, which returns the user's username and profile data (age, current savings, currency, risk level, investment horizon)
@router.get("/profile")
def get_user_profile(current_user=Depends(get_current_user)):
    profile = get_profile(current_user["id"])
    return {"username": current_user["username"], **(profile or {})}


# Route for updating the user's profile information, which allows the user to modify their age, current savings, currency, risk level, and investment horizon
@router.put("/profile")
def update_user_profile(body: ProfileUpdate, current_user=Depends(get_current_user)):
    update_profile(
        current_user["id"],
        body.age, body.current_savings,
        body.currency, body.risk_level, body.investment_horizon
    )
    return {"detail": "Profile updated"}


# Route for updating the user's account information, which allows the user to change their username, email, and password (with verification of the current password)
@router.put("/account")
def update_account(body: AccountUpdate, current_user=Depends(get_current_user)):
    user = get_user_by_username(current_user["username"])

    kwargs = {}
    if body.username:
        kwargs["username"] = body.username
    if body.email:
        kwargs["email"] = body.email
    if body.new_password:
        if not body.current_password or not verify_password(body.current_password, user["password_hash"]):
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        kwargs["password_hash"] = hash_password(body.new_password)

    if not kwargs:
        return {"detail": "No changes"}

    try:
        update_user(current_user["id"], **kwargs)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"detail": "Account updated"}


# Route for retrieving the user's avatar image, which returns the avatar as a PNG image if it exists, or raises a 404 error if no avatar is found
@router.get("/avatar")
def get_user_avatar(current_user=Depends(get_current_user)):
    avatar = get_avatar(current_user["id"])
    if not avatar:
        raise HTTPException(status_code=404, detail="No avatar")
    from fastapi.responses import Response
    return Response(content=avatar, media_type="image/png")


# Route for uploading and updating the user's avatar image, which accepts an image file, resizes it to a maximum of 256x256 pixels, and saves it as a PNG image in the database
@router.post("/avatar")
def upload_avatar(file: UploadFile = File(...), current_user=Depends(get_current_user)):
    img = Image.open(file.file).convert("RGB")
    img.thumbnail((256, 256))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    update_avatar(current_user["id"], buf.getvalue())
    return {"detail": "Avatar updated"}
