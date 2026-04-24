from fastapi import APIRouter

from app.services.news import fetch_news

router = APIRouter(prefix="/news", tags=["news"])


@router.get("")
async def get_news(limit: int = 20) -> list[dict]:
    return await fetch_news(max_items=limit)
