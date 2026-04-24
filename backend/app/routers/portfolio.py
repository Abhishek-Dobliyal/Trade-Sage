import asyncio
import logging

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import Holding
from app.services.csv_parser import parse_portfolio_csv
from app.services.market_data import get_bulk_prices

log = logging.getLogger(__name__)

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("/holdings")
async def list_holdings(db: AsyncSession = Depends(get_db)) -> list[dict]:
    result = await db.execute(select(Holding).order_by(Holding.asset_type, Holding.symbol))
    holdings = result.scalars().all()
    return [
        {
            "id": h.id,
            "symbol": h.symbol,
            "name": h.name,
            "asset_type": h.asset_type,
            "quantity": h.quantity,
            "avg_price": h.avg_price,
            "sector": h.sector,
            "imported_at": h.imported_at.isoformat(),
        }
        for h in holdings
    ]


@router.get("/csv-schema")
async def csv_schema() -> dict:
    return {
        "description": "Expected CSV format for portfolio import",
        "required_columns": ["symbol", "name", "type", "quantity", "avg_price"],
        "optional_columns": ["sector"],
        "type_values": ["STOCK", "MF"],
        "example_rows": [
            {"symbol": "RELIANCE", "name": "Reliance Industries", "type": "STOCK", "quantity": "10", "avg_price": "2450.50", "sector": "Energy"},
            {"symbol": "INF209K01YS4", "name": "SBI Bluechip Fund", "type": "MF", "quantity": "150.25", "avg_price": "68.30", "sector": ""},
        ],
    }


@router.post("/import")
async def import_csv(file: UploadFile, db: AsyncSession = Depends(get_db)) -> dict:
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")

    content = (await file.read()).decode("utf-8-sig")
    try:
        holdings = parse_portfolio_csv(content)
    except ValueError as e:
        log.warning("CSV import rejected: %s", e)
        raise HTTPException(status_code=400, detail=str(e))

    if not holdings:
        raise HTTPException(status_code=400, detail="No valid holdings found in CSV")

    await db.execute(delete(Holding))
    db.add_all(holdings)
    await db.commit()

    log.info("Imported %d holdings from %s", len(holdings), file.filename)
    return {"imported": len(holdings)}


@router.get("/valuation")
async def portfolio_valuation(db: AsyncSession = Depends(get_db)) -> dict:
    """Fetch live prices for all stock holdings and compute P&L."""
    result = await db.execute(select(Holding).order_by(Holding.asset_type, Holding.symbol))
    holdings = result.scalars().all()
    if not holdings:
        raise HTTPException(status_code=400, detail="No holdings found.")

    stock_symbols = [h.symbol for h in holdings if h.asset_type == "STOCK"]
    prices = await asyncio.to_thread(get_bulk_prices, stock_symbols) if stock_symbols else {}

    enriched = []
    total_invested = 0.0
    total_current = 0.0

    for h in holdings:
        invested = h.quantity * h.avg_price
        total_invested += invested
        entry = {
            "id": h.id,
            "symbol": h.symbol,
            "name": h.name,
            "asset_type": h.asset_type,
            "quantity": h.quantity,
            "avg_price": h.avg_price,
            "invested": round(invested, 2),
            "sector": h.sector,
        }
        price_data = prices.get(h.symbol)
        if price_data:
            current = h.quantity * price_data["current_price"]
            total_current += current
            entry.update({
                "current_price": price_data["current_price"],
                "current_value": round(current, 2),
                "pnl": round(current - invested, 2),
                "pnl_pct": round((current - invested) / invested * 100, 2) if invested else 0,
                "day_change_pct": price_data["day_change_pct"],
            })
        else:
            total_current += invested
            entry.update({
                "current_price": None,
                "current_value": round(invested, 2),
                "pnl": 0,
                "pnl_pct": 0,
                "day_change_pct": None,
            })
        enriched.append(entry)

    return {
        "holdings": enriched,
        "summary": {
            "total_invested": round(total_invested, 2),
            "total_current": round(total_current, 2),
            "total_pnl": round(total_current - total_invested, 2),
            "total_pnl_pct": round(
                (total_current - total_invested) / total_invested * 100, 2
            ) if total_invested else 0,
        },
    }


@router.delete("/holdings")
async def clear_holdings(db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(delete(Holding))
    await db.commit()
    log.info("Cleared %d holdings", result.rowcount)
    return {"deleted": result.rowcount}
