import uuid
import os
from fastapi import APIRouter, Request, status, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import logging
# from .db import get_supabase
from model.users import UserRegisterRequest
from .auth import hash_password
import sys
import os
from utils.email_sender import send_verification_email
from .db import get_supabase
from fastapi import HTTPException

router = APIRouter()


@router.post("/register")
async def register_user(request: Request):
    try:
        data_json = await request.json()
        logging.info(f"Received register data: {data_json}")
        data = UserRegisterRequest(**data_json)
    except ValidationError as ve:
        logging.error(f"Validation error: {ve}")
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": ve.errors()})
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(e)})

    # Cek apakah email sudah dipakai
    existing = get_supabase().table("users").select(
        "id").eq("email", data.email).execute()
    logging.info(f"Existing data for email {data.email}: {existing.data}")
    if existing.data and len(existing.data) > 0:
        raise HTTPException(
            status_code=400, detail="Email already registered.")

    hashed_pw = hash_password(data.password)

    # Generate verification token
    verification_token = str(uuid.uuid4())

    # Insert user with verified=False and verification_token
    response = get_supabase().table("users").insert({
        "name": data.name,
        "gender": data.gender,
        "date": data.date.isoformat(),
        "email": data.email,
        "password_hash": hashed_pw,
        "verified": False,
        "verification_token": verification_token
    }).execute()

    if response.data is None or len(response.data) == 0:
        raise HTTPException(status_code=500, detail="Gagal mendaftarkan user")

    # Send verification email
    frontend_url = os.getenv(
        "FRONTEND_URL", "https://epicare-fullstack.onrender.com")
    print(f"Using FRONTEND_URL: {frontend_url}")
    verification_link = f"{frontend_url}/verify-email?token={verification_token}"

    try:
        send_verification_email(data.email, verification_link)
    except Exception as e:
        logging.error(f"Failed to send verification email: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to send verification email")

    return {"message": "User registered successfully. Please check your email to verify your account before logging in."}


@router.post("/request-password-reset")
async def request_password_reset(request: Request):
    try:
        data_json = await request.json()
        email = data_json.get("email")
        if not email:
            return JSONResponse(status_code=400, content={"detail": "Email is required"})

        user_response = get_supabase().table("users").select(
            "*").eq("email", email).execute()
        if not user_response.data or len(user_response.data) == 0:
            # For security, do not reveal if email is not registered
            return JSONResponse(status_code=200, content={"message": "A reset link has been sent to email."})

        user = user_response.data[0]

        reset_token = str(uuid.uuid4())
        from datetime import datetime, timedelta
        reset_token_expiry = (datetime.utcnow() +
                              timedelta(hours=1)).isoformat()

        update_response = get_supabase().table("users").update({
            "reset_token": reset_token,
            "reset_token_expiry": reset_token_expiry
        }).eq("id", user["id"]).execute()

        if update_response.data is None or len(update_response.data) == 0:
            return JSONResponse(status_code=500, content={"detail": "Failed to set reset token"})

        frontend_url = os.getenv(
            "FRONTEND_URL", "https://epicare-fullstack.onrender.com/frontend")
        reset_link = f"{frontend_url}/reset-password.html?token={reset_token}"

        try:
            # Use a custom function to send password reset email with correct subject
            from utils.email_sender import send_password_reset_email
            send_password_reset_email(email, reset_link)
        except Exception as e:
            logging.error(f"Failed to send password reset email: {e}")
            return JSONResponse(status_code=500, content={"detail": "Failed to send password reset email"})

        return JSONResponse(status_code=200, content={"message": "If the email is registered, a reset link has been sent."})

    except Exception as e:
        logging.error(f"Unexpected error in request_password_reset: {e}")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@router.post("/reset-password")
async def reset_password(request: Request):
    try:
        data_json = await request.json()
        token = data_json.get("token")
        new_password = data_json.get("new_password")

        if not token or not new_password:
            return JSONResponse(status_code=400, content={"detail": "Token and new password are required"})

        user_response = get_supabase().table("users").select(
            "*").eq("reset_token", token).execute()
        if not user_response.data or len(user_response.data) == 0:
            return JSONResponse(status_code=400, content={"detail": "Invalid or expired reset token"})

        user = user_response.data[0]

        from datetime import datetime, timezone
        if not user.get("reset_token_expiry"):
            return JSONResponse(status_code=400, content={"detail": "Invalid or expired reset token"})

        expiry = datetime.fromisoformat(user["reset_token_expiry"])
        if expiry.replace(tzinfo=timezone.utc) < datetime.utcnow().replace(tzinfo=timezone.utc):
            return JSONResponse(status_code=400, content={"detail": "Reset token has expired"})

        hashed_pw = hash_password(new_password)

        update_response = get_supabase().table("users").update({
            "password_hash": hashed_pw,
            "reset_token": None,
            "reset_token_expiry": None
        }).eq("id", user["id"]).execute()

        if update_response.data is None or len(update_response.data) == 0:
            return JSONResponse(status_code=500, content={"detail": "Failed to update password"})

        return JSONResponse(status_code=200, content={"message": "Password has been reset successfully."})

    except Exception as e:
        logging.error(f"Unexpected error in reset_password: {e}")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@router.get("/verify-email")
async def verify_email(token: str):
    # Find user by verification token
    user_response = get_supabase().table("users").select(
        "*").eq("verification_token", token).execute()
    if not user_response.data or len(user_response.data) == 0:
        raise HTTPException(
            status_code=400, detail="Invalid or expired verification token")

    user = user_response.data[0]

    # Update user to verified
    update_response = get_supabase().table("users").update({
        "verified": True,
        "verification_token": None
    }).eq("id", user["id"]).execute()

    if update_response.data is None or len(update_response.data) == 0:
        raise HTTPException(status_code=500, detail="Failed to verify email")

    return {"message": "Email verified successfully. You can now log in."}
