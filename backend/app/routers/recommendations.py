import asyncio
import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import Holding, Recommendation
from app.prompts.system import RECOMMENDATION_PROMPT, SYSTEM_PROMPT
from app.services.llm import chat_completion
from app.services.market_data import get_index_quotes
from app.services.news import fetch_news

log = logging.getLogger(__name__)

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post("/generate")
async def generate_recommendations(db: AsyncSession = Depends(get_db)) -> list[dict]:
    result = await db.execute(select(Holding))
    holdings = result.scalars().all()
    if not holdings:
        raise HTTPException(status_code=400, detail="No holdings found. Import your portfolio first.")

    holdings_text = "\n".join(
        f"- {h.symbol} ({h.name}): {h.quantity} units @ ₹{h.avg_price:.2f} | {h.asset_type}"
        for h in holdings
    )

    try:
        news = await fetch_news(max_items=5)
        news_text = "\n".join(f"- {n['title']}" for n in news)
    except Exception:
        log.exception("Failed to fetch news for recommendations")
        news_text = "News unavailable."

    market_text = "Market indices unavailable."
    try:
        indices = await asyncio.to_thread(get_index_quotes)
        if indices:
            market_text = "\n".join(
                f"- {i['name']}: {i['value']} ({i['change_pct']:+.2f}%)" for i in indices
            )
    except Exception:
        log.exception("Failed to fetch market indices for recommendations")

    prompt = RECOMMENDATION_PROMPT.format(
        holdings=holdings_text,
        market_context=market_text,
        news_summary=news_text,
    )

    response = await chat_completion(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
        stream=False,
    )

    try:
        content = response["content"]
        # Strip markdown code fences if present
        if "```" in content:
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        recs_data = json.loads(content.strip())
    except (json.JSONDecodeError, IndexError):
        log.error("Failed to parse LLM recommendation response: %s", content[:500])
        raise HTTPException(
            status_code=500,
            detail="Failed to parse LLM response into recommendations.",
        )

    # Persist recommendations
    await db.execute(delete(Recommendation))
    recs = []
    for r in recs_data:
        rec = Recommendation(
            symbol=r.get("symbol", ""),
            name=r.get("name", ""),
            action=r.get("action", "HOLD"),
            rationale=r.get("rationale", ""),
            confidence=float(r.get("confidence", 0)),
            target_price=r.get("target_price"),
            stop_loss=r.get("stop_loss"),
        )
        db.add(rec)
        recs.append(r)
    await db.commit()
    return recs


@router.get("")
async def list_recommendations(db: AsyncSession = Depends(get_db)) -> list[dict]:
    result = await db.execute(
        select(Recommendation).order_by(Recommendation.created_at.desc())
    )
    recs = result.scalars().all()
    return [
        {
            "id": r.id,
            "symbol": r.symbol,
            "name": r.name,
            "action": r.action,
            "rationale": r.rationale,
            "confidence": r.confidence,
            "target_price": r.target_price,
            "stop_loss": r.stop_loss,
            "created_at": r.created_at.isoformat(),
        }
        for r in recs
    ]
