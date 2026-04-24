import asyncio
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import Watchlist
from app.services.market_data import get_stock_price

log = logging.getLogger(__name__)

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


class WatchlistAdd(BaseModel):
    symbol: str
    name: str
    notes: str = ""


@router.get("")
async def list_watchlist(db: AsyncSession = Depends(get_db)) -> list[dict]:
    result = await db.execute(select(Watchlist).order_by(Watchlist.added_at.desc()))
    items = result.scalars().all()

    symbols = [w.symbol for w in items]
    prices = {}
    if symbols:
        try:
            prices = await asyncio.to_thread(_fetch_prices, symbols)
        except Exception:
            log.exception("Failed to fetch watchlist prices")

    return [
        {
            "id": w.id,
            "symbol": w.symbol,
            "name": w.name,
            "notes": w.notes,
            "added_at": w.added_at.isoformat(),
            **(prices.get(w.symbol, {})),
        }
        for w in items
    ]


def _fetch_prices(symbols: list[str]) -> dict[str, dict]:
    results = {}
    for symbol in symbols:
        price = get_stock_price(symbol)
        if price:
            results[symbol] = {
                "current_price": price["current_price"],
                "day_change": price["day_change"],
                "day_change_pct": price["day_change_pct"],
            }
    return results


@router.post("")
async def add_to_watchlist(
    item: WatchlistAdd, db: AsyncSession = Depends(get_db)
) -> dict:
    existing = await db.execute(
        select(Watchlist).where(Watchlist.symbol == item.symbol.upper())
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"{item.symbol} already in watchlist")

    entry = Watchlist(
        symbol=item.symbol.upper(),
        name=item.name,
        notes=item.notes,
    )
    db.add(entry)
    await db.commit()
    log.info("Added %s to watchlist", item.symbol)
    return {"id": entry.id, "symbol": entry.symbol, "name": entry.name}


@router.delete("/{symbol}")
async def remove_from_watchlist(
    symbol: str, db: AsyncSession = Depends(get_db)
) -> dict:
    result = await db.execute(
        delete(Watchlist).where(Watchlist.symbol == symbol.upper())
    )
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail=f"{symbol} not found in watchlist")
    log.info("Removed %s from watchlist", symbol)
    return {"removed": symbol.upper()}
