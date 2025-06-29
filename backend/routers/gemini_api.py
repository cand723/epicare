import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY belum diset di file .env")

genai.configure(api_key=GEMINI_API_KEY)

router = APIRouter()


class ChatRequest(BaseModel):
    messages: list[str]  # list of strings with roles


@router.post("/chat")
async def chat(req: ChatRequest):
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        full_prompt = "\n".join(req.messages)
        response = model.generate_content(full_prompt)
        return {"reply": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
