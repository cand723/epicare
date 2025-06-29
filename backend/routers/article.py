from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from backend.routers.register.db import get_supabase

router = APIRouter()


@router.get("/api/articles")
async def get_articles():
    try:
        response = get_supabase().table("articles").select(
            "*").order("published_at", desc=True).execute()
        if response.data is None:
            return JSONResponse(status_code=404, content={"detail": "No articles found"})
        return response.data
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch articles: {e}")


@router.get("/api/articles/{article_id}")
async def get_article(article_id: str):
    try:
        response = get_supabase().table("articles").select(
            "*").eq("id", article_id).execute()
        if not response.data or len(response.data) == 0:
            return JSONResponse(status_code=404, content={"detail": "Article not found"})
        return response.data[0]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch article: {e}")
