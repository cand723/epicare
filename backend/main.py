from backend.routers.analisis_rontgen_api import router as rontgen_router
from backend.utils.load_env import load_environment
from backend.routers.article import router as article_router
from backend.routers.chat_history import router as chat_history_router
from backend.routers.article_admin import router as article_admin_router
from backend.routers.oauth.google import router as google_router
from backend.routers.register.login import router as login_router
from backend.routers.register.register import router as register_router
from backend.routers.analisis_gejala_api import router as gejala_router
from backend.routers.register.login_admin import router as login_admin_router
from backend.routers.gemini_api import router as gemini_router
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exception_handlers import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.requests import Request as FastAPIRequest
from fastapi.exceptions import RequestValidationError
from fastapi import status
from fastapi.responses import Response
from fastapi.exceptions import HTTPException as FastAPIHTTPException

import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

load_environment()

app = FastAPI()

# Path ke frontend HTML
app.mount("/frontend", StaticFiles(directory="./frontend"), name="frontend")
templates = Jinja2Templates(directory="./frontend")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://epicare-fullstack.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session Middleware
app.add_middleware(SessionMiddleware, secret_key="random_secret_key")

# Router
app.include_router(gemini_router)
app.include_router(gejala_router)
app.include_router(register_router)
app.include_router(login_router)
app.include_router(google_router)
app.include_router(article_router)
app.include_router(chat_history_router)
app.include_router(rontgen_router)
app.include_router(article_admin_router)
app.include_router(login_admin_router)
# Dependency untuk cek login session


def get_current_user(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 401:
        return RedirectResponse(url="/frontend/login.html")
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.get("/")
async def root(request: Request):
    user = request.session.get("user")
    if user:
        return RedirectResponse(url="/frontend/beranda.html")
    return RedirectResponse(url="/frontend/index.html")


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    response = RedirectResponse(url="/frontend/login.html")
    response.delete_cookie(key="session")
    return response


# Contoh route yang diproteksi (misalnya chatbot)
@app.get("/chatbot-protected")
async def chatbot(request: Request, user: dict = Depends(get_current_user)):
    return RedirectResponse(url="/frontend/chatbot.html")


@app.get("/chatbot")
async def chatbot_page(request: Request, user: dict = Depends(get_current_user)):
    return templates.TemplateResponse("chatbot.html", {"request": request})


@app.get("/sistem_analisis")
async def sistem_analisis_page(request: Request, user: dict = Depends(get_current_user)):
    return templates.TemplateResponse("sistem_analisis.html", {"request": request})


@app.get("/sistem_analisis_page2")
async def sistem_analisis_page2(request: Request, user: dict = Depends(get_current_user)):
    return templates.TemplateResponse("sistem_analisis_page2.html", {"request": request})


@app.get("/beranda")
async def beranda_page(request: Request, user: dict = Depends(get_current_user)):
    return RedirectResponse(url="/frontend/beranda.html")


@app.get("/artikel")
async def artikel_page(request: Request):
    return templates.TemplateResponse("article-list.html", {"request": request})


@app.get("/api/user")
async def get_user(user: dict = Depends(get_current_user)):
    return user
