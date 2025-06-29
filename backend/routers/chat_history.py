from fastapi import APIRouter, HTTPException, status  # Impor status
from routers.register.db import get_supabase
from typing import List
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime  # Impor datetime di sini

router = APIRouter(
    prefix="/chat_history",
    tags=["chat_history"]
)


@router.get("/test")
async def test_endpoint():
    return {"message": "Chat history router is working"}


class Chat(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    created_at: str


class Message(BaseModel):
    id: UUID
    chat_id: UUID
    sender: str
    content: str
    created_at: str


class ChatCreateRequest(BaseModel):
    user_id: UUID
    title: str


class MessageCreateRequest(BaseModel):
    chat_id: UUID
    sender: str
    content: str


class ChatUpdateRequest(BaseModel):
    title: str


@router.get("/chats/{user_id}", response_model=List[Chat])
async def get_chats(user_id: UUID):
    response = get_supabase()\
        .from_("chats")\
        .select("*")\
        .eq("user_id", str(user_id))\
        .order("created_at", desc=True)\
        .execute()
    status_code = getattr(response, 'status_code', None)
    if status_code is not None and status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch chats")
    if response.data is None:
        return []  # Mengembalikan list kosong jika tidak ada data, bukan 500
    return response.data


@router.post("/chats", response_model=Chat)
async def create_chat(chat: ChatCreateRequest):
    now_iso = datetime.utcnow().isoformat()
    response = get_supabase().from_("chats").insert({
        "user_id": str(chat.user_id),
        "title": chat.title,
        "created_at": now_iso
    }).execute()
    status_code = getattr(response, 'status_code', None)
    if status_code is not None and status_code != 201:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create chat")
    if response.data is None or len(response.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create chat")
    return response.data[0]


@router.get("/messages/{chat_id}", response_model=List[Message])
async def get_messages(chat_id: UUID):
    response = get_supabase()\
        .from_("messages")\
        .select("*")\
        .eq("chat_id", str(chat_id))\
        .order("created_at", desc=False)\
        .execute()
    status_code = getattr(response, 'status_code', None)
    if status_code is not None and status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch messages")
    if response.data is None:
        return []  # Mengembalikan list kosong jika tidak ada data, bukan 500
    return response.data


@router.post("/messages", response_model=Message)
async def create_message(message: MessageCreateRequest):
    now_iso = datetime.utcnow().isoformat()
    response = get_supabase().from_("messages").insert({
        "chat_id": str(message.chat_id),
        "sender": message.sender,
        "content": message.content,
        "created_at": now_iso
    }).execute()
    status_code = getattr(response, 'status_code', None)
    if status_code is not None and status_code != 201:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create message")
    if response.data is None or len(response.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create message")
    return response.data[0]


@router.patch("/chats/{chat_id}", response_model=Chat)
async def update_chat_title(chat_id: UUID, chat_update: ChatUpdateRequest):
    response = get_supabase().from_("chats").update({
        "title": chat_update.title
    }).eq("id", str(chat_id)).execute()

    # Perbaikan: Jika data kosong, berarti chat tidak ditemukan
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

    status_code = getattr(response, 'status_code', None)
    if status_code is not None and status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update chat title")

    return response.data[0]


@router.delete("/chats/{chat_id}")
async def delete_chat(chat_id: UUID):
    # Hapus pesan yang terkait dengan chat terlebih dahulu
    response_messages = get_supabase().from_("messages").delete().eq(
        "chat_id", str(chat_id)).execute()

    # Supabase mengembalikan status 200 bahkan jika tidak ada baris yang dihapus.
    # Kita tidak perlu memeriksa data di sini secara ketat, karena mungkin tidak ada pesan.
    status_code_messages = getattr(response_messages, 'status_code', None)
    # 204 No Content juga bisa
    if status_code_messages is not None and status_code_messages not in [200, 204]:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to delete associated messages")

    # Kemudian, hapus chat itu sendiri
    response_chat = get_supabase().from_("chats").delete().eq(
        "id", str(chat_id)).execute()

    # Perbaikan: Jika data kosong, berarti chat tidak ditemukan
    if not response_chat.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Chat not found or failed to delete")

    status_code_chat = getattr(response_chat, 'status_code', None)
    if status_code_chat is not None and status_code_chat != 200:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete chat")

    return {"message": "Chat deleted successfully"}
