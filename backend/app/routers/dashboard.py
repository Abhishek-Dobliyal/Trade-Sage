import asyncio
import logging

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import Holding, Recommendation
from app.services.market_data import get_index_quotes
from app.services.news import fetch_news

log = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _build_portfolio_summary(holdings: list[Holding]) -> dict:
    total_invested = sum(h.quantity * h.avg_price for h in holdings)
    sector_map: dict[str, float] = {}
    for h in holdings:
        sector = h.sector or "Uncategorized"
        sector_map[sector] = sector_map.get(sector, 0) + (h.quantity * h.avg_price)

    stocks = [h for h in holdings if h.asset_type == "STOCK"]
    mfs = [h for h in holdings if h.asset_type == "MF"]

    return {
        "total_invested": round(total_invested, 2),
        "holdings_count": len(holdings),
        "stocks_count": len(stocks),
        "mf_count": len(mfs),
        "sector_allocation": {
            sector: round(value / total_invested * 100, 2) if total_invested else 0
            for sector, value in sorted(sector_map.items(), key=lambda x: x[1], reverse=True)
        },
    }


@router.get("")
async def dashboard(db: AsyncSession = Depends(get_db)) -> dict:
    holdings_result, recs_result = await asyncio.gather(
        db.execute(select(Holding)),
        db.execute(
            select(Recommendation).order_by(Recommendation.created_at.desc()).limit(5)
        ),
    )
    holdings = holdings_result.scalars().all()
    recommendations = recs_result.scalars().all()

    results = await asyncio.gather(
        asyncio.to_thread(get_index_quotes),
        fetch_news(max_items=5),
        return_exceptions=True,
    )

    if isinstance(results[0], Exception):
        log.exception("Failed to fetch indices for dashboard", exc_info=results[0])
        indices = []
    else:
        indices = results[0]

    if isinstance(results[1], Exception):
        log.exception("Failed to fetch news for dashboard", exc_info=results[1])
        news = []
    else:
        news = results[1]

    return {
        "portfolio": _build_portfolio_summary(holdings) if holdings else None,
        "indices": indices,
        "news": news,
        "recommendations": [
            {
                "symbol": r.symbol,
                "name": r.name,
                "action": r.action,
                "rationale": r.rationale,
                "confidence": r.confidence,
                "created_at": r.created_at.isoformat(),
            }
            for r in recommendations
        ],
    }
