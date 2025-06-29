from fastapi import status, APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import traceback
from pydantic import BaseModel
from passlib.context import CryptContext  # Impor CryptContext

# Asumsi get_supabase() ada di db.py
from .db import get_supabase

# Jika LoginInput sudah ada di model/LoginInput.py, Anda bisa mengimpornya dari sana
# from model.LoginInput import LoginInput


class LoginInput(BaseModel):
    email: str
    password: str


router = APIRouter()

# Konfigurasi passlib untuk hashing password
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifikasi password plaintext terhadap hash bcrypt."""
    return pwd_context.verify(plain_password, hashed_password)


@router.post("/admin-login")
async def login_admin(login_input: LoginInput, request: Request = None):
    """
    Endpoint untuk login admin.
    Memverifikasi kredensial admin terhadap tabel 'admin' di Supabase menggunakan hash password.
    """
    try:
        supabase = get_supabase()
        email = login_input.email
        password = login_input.password

        # Mengambil data admin dari tabel 'admin'
        # Sekarang kita akan mengambil 'password_hash'
        response = supabase.table("admin").select(
            "id, email, password_hash"  # Ambil kolom yang dibutuhkan, termasuk password_hash
        ).eq("email", email).execute()

        admin_data = response.data

        if not admin_data:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"success": False,
                         "message": "Invalid email or password."}
            )

        admin = admin_data[0]

        # --- VERIFIKASI PASSWORD MENGGUNAKAN HASH ---
        # Memverifikasi password yang dimasukkan dengan hash yang tersimpan
        if not verify_password(password, admin.get("password_hash", "")):
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"success": False,
                         "message": "Invalid email or password."}
            )
        # --- AKHIR VERIFIKASI PASSWORD ---

        # Jika login berhasil, simpan informasi admin ke sesi
        if request:
            request.session["admin_user"] = {
                "id": admin["id"],
                "email": admin["email"],
                "role": "admin"
            }
            print(f"Admin logged in: {admin['email']}")

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "message": "Admin login successful!",
                "admin": {
                    "id": admin["id"],
                    "email": admin["email"]
                }
            }
        )

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": f"An unexpected error occurred: {type(e).__name__} - {e}"}
        )
