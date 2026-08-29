from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query # Libraries for building API routes, handling dependencies, raising HTTP exceptions, and managing file uploads
from PIL import Image # Library for image processing, used to handle avatar images
import io # Library for handling input/output operations, used to manage image data in memory
from backend.api.schemas.schemas import ProfileUpdate, AccountUpdate, TransactionCreate, TransactionResponse # Pydantic models for validating and managing user profile, account, and transaction requests
from backend.auth.database import get_profile, update_profile, get_avatar, update_avatar, delete_avatar, update_user, get_user_by_id, create_transaction, update_transaction, delete_transaction, load_transactions # Database functions for retrieving and updating user data
from backend.auth.hash import hash_password, verify_password # Functions for hashing and verifying passwords
from backend.auth.jwt import get_current_user # Dependency function to get the current authenticated user

router = APIRouter() # Class used to group related API routes together



@router.get("/transactions", response_model=list[TransactionResponse])
def get_user_transactions(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    current_user=Depends(get_current_user),
):
    return load_transactions(current_user["id"], year, month)


@router.post("/transactions", response_model=TransactionResponse, status_code=201)
def add_user_transaction(body: TransactionCreate, current_user=Depends(get_current_user)):
    if body.kind not in {"income", "expense"}:
        raise HTTPException(status_code=400, detail="Transaction type must be income or expense")
    if body.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than zero")
    return create_transaction(
        current_user["id"],
        body.entry_date,
        body.kind,
        body.amount,
        body.description,
        body.currency.upper(),
        body.category,
    )


@router.put("/transactions/{transaction_id}", response_model=TransactionResponse)
def update_user_transaction(transaction_id: int, body: TransactionCreate, current_user=Depends(get_current_user)):
    if body.kind not in {"income", "expense"}:
        raise HTTPException(status_code=400, detail="Transaction type must be income or expense")
    if body.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than zero")
    try:
        return update_transaction(
            current_user["id"],
            transaction_id,
            body.entry_date,
            body.kind,
            body.amount,
            body.description,
            body.currency.upper(),
            body.category,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/transactions/{transaction_id}")
def delete_user_transaction(transaction_id: int, current_user=Depends(get_current_user)):
    if not delete_transaction(current_user["id"], transaction_id):
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"detail": "Transaction deleted"}


## Route for retrieving the user's profile information, which returns the user's username and profile data (age, current savings, currency, risk level, investment horizon)
@router.get("/profile")
def get_user_profile(current_user=Depends(get_current_user)):
    print("Current user ID:", current_user["id"])
    profile = get_profile(current_user["id"])
    return profile or {"username": current_user["username"], "current_user_id": current_user["id"]}


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
    user = get_user_by_id(current_user["id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

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


@router.delete("/avatar")
def delete_user_avatar(current_user=Depends(get_current_user)):
    delete_avatar(current_user["id"])
    return {"detail": "Avatar deleted"}
