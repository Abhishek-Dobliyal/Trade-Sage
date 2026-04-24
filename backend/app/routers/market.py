import asyncio
import logging
from functools import partial

from fastapi import APIRouter, HTTPException

from app.services.market_data import get_index_quotes, get_stock_history, get_stock_price

log = logging.getLogger(__name__)

router = APIRouter(prefix="/market", tags=["market"])


def _run_sync(func, *args, **kwargs):
    """Run a sync function in a thread to avoid blocking the event loop."""
    return asyncio.to_thread(partial(func, *args, **kwargs))


@router.get("/indices")
async def indices() -> list[dict]:
    return await _run_sync(get_index_quotes)


@router.get("/quote/{symbol}")
async def quote(symbol: str) -> dict:
    result = await _run_sync(get_stock_price, symbol.upper())
    if result is None:
        raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
    return result


@router.get("/history/{symbol}")
async def history(symbol: str, period: str = "6mo", interval: str = "1d") -> list[dict]:
    return await _run_sync(get_stock_history, symbol.upper(), period, interval)
