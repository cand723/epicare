from fastapi import status
from fastapi.responses import HTMLResponse, RedirectResponse
import traceback
from fastapi import HTTPException, APIRouter, Request
from fastapi.responses import JSONResponse
from .auth import verify_password
from model.LoginInput import LoginInput
from .db import get_supabase
router = APIRouter()


# def get_supabase():
#     # Import supabase client inside the function to delay initialization and ease mocking in tests
#     from .db import get_supabase
#     return supabase


@router.post("/login")
async def login_user(login_input: LoginInput, request: Request = None):
    try:
        supabase = get_supabase()
        email = login_input.email
        password = login_input.password

        response = supabase.table("users").select(
            "*").eq("email", email).execute()
        user_data = response.data

        if not user_data:
            return JSONResponse(status_code=status.HTTP_200_OK, content={"success": False, "message": "Invalid email or password"})

        user = user_data[0]

        if not verify_password(password, user["password_hash"]):
            return JSONResponse(status_code=status.HTTP_200_OK, content={"success": False, "message": "Invalid email or password"})

        if not user.get("verified", False):
            return JSONResponse(status_code=status.HTTP_200_OK, content={"success": False, "message": "Please verify your email before logging in."})

        if request:
            request.session["user"] = {
                "id": user["id"],
                "email": user["email"],
                "name": user.get("name", "")
            }

        return JSONResponse(status_code=status.HTTP_200_OK, content={
            "success": True,
            "user": {
                "id": user["id"],
                "email": user["email"],
                "name": user.get("name", "")
            }
        })

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": f"Unexpected error: {type(e).__name__} - {e}"})
