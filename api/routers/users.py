from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from PIL import Image
import io
from api.schemas.schemas import ProfileUpdate, AccountUpdate
from auth.database import get_profile, update_profile, get_avatar, update_avatar, update_user, get_user_by_username
from auth.hash import hash_password, verify_password
from auth.jwt import get_current_user

router = APIRouter()


@router.get("/profile")
def get_user_profile(current_user=Depends(get_current_user)):
    profile = get_profile(current_user["id"])
    return {"username": current_user["username"], **(profile or {})}


@router.put("/profile")
def update_user_profile(body: ProfileUpdate, current_user=Depends(get_current_user)):
    update_profile(
        current_user["id"],
        body.age, body.current_savings,
        body.currency, body.risk_level, body.investment_horizon
    )
    return {"detail": "Profile updated"}


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


@router.get("/avatar")
def get_user_avatar(current_user=Depends(get_current_user)):
    avatar = get_avatar(current_user["id"])
    if not avatar:
        raise HTTPException(status_code=404, detail="No avatar")
    from fastapi.responses import Response
    return Response(content=avatar, media_type="image/png")


@router.post("/avatar")
def upload_avatar(file: UploadFile = File(...), current_user=Depends(get_current_user)):
    img = Image.open(file.file).convert("RGB")
    img.thumbnail((256, 256))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    update_avatar(current_user["id"], buf.getvalue())
    return {"detail": "Avatar updated"}
