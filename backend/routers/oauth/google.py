import logging
from authlib.integrations.base_client.errors import OAuthError
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from authlib.integrations.starlette_client import OAuth
from dotenv import load_dotenv
from backend.model.users import UserRegisterRequest
from supabase import create_client, Client
import os

load_dotenv()

router = APIRouter()

# Setup OAuth client
oauth = OAuth()
oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# Setup Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)


@router.get("/auth/google")
async def login_via_google(request: Request):
    redirect_uri = request.url_for('auth_google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/auth/google/callback")
async def auth_google_callback(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
        user = token.get('userinfo')

        if not user:
            return HTMLResponse("<h2>Error: User info not found in token.</h2>", status_code=400)

        email = user["email"]

        # Cek apakah user sudah terdaftar di Supabase
        existing = supabase.table("users").select(
            "id").eq("email", email).execute()

        # Tentukan redirect URL berdasarkan ada/tidaknya data user
        if existing.data:
            user_id = existing.data[0]['id']
            redirect_url = "/frontend/beranda.html"  # Sudah terdaftar → langsung ke app
        else:
            user_id = None
            # Belum terdaftar → lengkapi data
            redirect_url = "/frontend/lengkapi-register.html"

        return HTMLResponse(f"""
        <html>
            <head><title>Redirecting...</title></head>
            <body>
                <script>
                    sessionStorage.setItem('user', JSON.stringify({{
                        'id': '{user_id}',
                        'name': '{user['name']}',
                        'email': '{user['email']}',
                        'picture': '{user['picture']}'
                    }}));
                    window.location.href = '{redirect_url}';
                </script>
            </body>
        </html>
        """)
    except OAuthError as e:
        logging.error(
            f"OAuth error during Google callback: {e.error} - {e.description}")
        return HTMLResponse(f"<h2>OAuth Error: {e.error}</h2><p>{e.description}</p>", status_code=400)


@router.post("/oauth-complete-register")
async def complete_google_register(request: Request, data: UserRegisterRequest):
    # Cek apakah email sudah dipakai
    existing = supabase.table("users").select(
        "id").eq("email", data.email).execute()
    if existing.data:
        raise HTTPException(
            status_code=400, detail="Email already registered.")

    # Insert user ke Supabase
    response = supabase.table("users").insert({
        "name": data.name,
        "email": data.email,
        "gender": data.gender,
        "date": data.date.isoformat(),  # Asumsikan 'birthdate' adalah tipe date
        "password_hash": None  # Karena menggunakan OAuth, password_hash tidak diperlukan
    }).execute()

    if response.data is None or len(response.data) == 0:
        raise HTTPException(status_code=500, detail="Gagal mendaftarkan user")

    return JSONResponse(status_code=200, content={"message": "User registered successfully"})
