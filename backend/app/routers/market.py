import asyncio
import logging
import re

from fastapi import APIRouter, HTTPException

from app.services.market_data import get_index_quotes, get_stock_history, get_stock_price

log = logging.getLogger(__name__)

router = APIRouter(prefix="/market", tags=["market"])

INVALID_SYMBOL_RE = re.compile(r'^\d{6,}$|^[A-Z]{1,2}\d+$')


def is_valid_symbol(symbol: str) -> bool:
    s = symbol.upper()
    if INVALID_SYMBOL_RE.match(s):
        return False
    if len(s) < 2 or len(s) > 15:
        return False
    return True


@router.get("/indices")
async def indices() -> list[dict]:
    return await asyncio.to_thread(get_index_quotes)


@router.get("/quote/{symbol}")
async def quote(symbol: str) -> dict:
    if not is_valid_symbol(symbol):
        raise HTTPException(status_code=404, detail=f"Invalid symbol: {symbol}")
    result = await asyncio.to_thread(get_stock_price, symbol.upper())
    if result is None:
        raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
    return result


@router.get("/history/{symbol}")
async def history(symbol: str, period: str = "6mo", interval: str = "1d") -> list[dict]:
    if not is_valid_symbol(symbol):
        raise HTTPException(status_code=404, detail=f"Invalid symbol: {symbol}")
    return await asyncio.to_thread(get_stock_history, symbol.upper(), period, interval)
