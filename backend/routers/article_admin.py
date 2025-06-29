from backend.routers.register.db import get_supabase
from uuid import uuid4
from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter()

# Enable CORS supaya frontend bisa akses API tanpa masalah
# router.add_middleware(
#     CORSMiddleware,
#     # ganti * dengan domain frontend-mu kalau sudah produksi
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# Model artikel untuk request dan response


class Article(BaseModel):
    id: Optional[str] = None
    author: str
    title: str
    url: str
    url_to_image: str
    published_at: Optional[datetime] = None
    description: str
    content: str


class ArticleUpdate(BaseModel):
    author: str
    title: str
    url: str
    url_to_image: str
    published_at: Optional[datetime] = None
    description: str
    content: str


# Data simulasi artikel (biasanya dari database)
articles = [
    {
        "id": 1,
        "author": "Rian Hidayat",
        "title": "Inovasi Teknologi AI di Era Digital",
        "url": "https://example.com/ai-era-digital",
        "description": "Membahas perkembangan terbaru dalam kecerdasan buatan dan dampaknya pada masyarakat modern.",
        "content": "Isi lengkap artikel tentang AI di era digital..."
    }
]

# Fungsi bantu untuk cari artikel berdasarkan ID


def get_article_by_id(article_id: int):
    for article in articles:
        if article["id"] == article_id:
            return article
    return None

# API: List semua artikel


@router.get("/admin-article", response_model=List[Article])
def read_articles():
    res = get_supabase().table("articles").select(
        "*").order("published_at", desc=True).execute()
    return res.data


# API: Tambah artikel baru


@router.post("/admin-article", response_model=Article)
def create_article(article: Article):
    article_id = str(uuid4())

    data = {
        "id": article_id,
        "author": article.author,
        "title": article.title,
        "url": article.url,
        "url_to_image": article.url_to_image,
        "published_at": article.published_at.isoformat() if article.published_at else None,
        "description": article.description,
        "content": article.content
    }

    res = get_supabase().table("articles").insert(data).execute()

    if res.data is None or len(res.data) == 0:
        raise HTTPException(status_code=500, detail="Gagal menyimpan artikel")

    return res.data[0]

# API: Update artikel berdasarkan ID


@router.put("/admin-article/{article_id}", response_model=dict)
def update_article(article_id: str, updated_article: ArticleUpdate):
    data = updated_article.dict(exclude_unset=True)

    if "published_at" in data and data["published_at"]:
        data["published_at"] = data["published_at"].isoformat()

    res = get_supabase().table("articles").update(
        data).eq("id", article_id).execute()

    # Debugging
    print("Update response from get_supabase():", res)

    if not res.data:
        raise HTTPException(
            status_code=404, detail="Gagal memperbarui artikel (ID tidak ditemukan)")

    # Jika datanya tidak sesuai ekspektasi
    if isinstance(res.data, list):
        return res.data[0]
    return res.data  # fallback


# API: Hapus artikel berdasarkan ID


@router.delete("/admin-article/{article_id}")
def delete_article(article_id: str):
    res = get_supabase().table("articles").delete().eq("id", article_id).execute()

    if not res.data:
        raise HTTPException(
            status_code=404, detail="Artikel tidak ditemukan atau gagal dihapus")

    return {"detail": "Artikel berhasil dihapus"}
