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


def _parse_llm_json(content: str) -> list[dict]:
    """Extract a list of recommendation dicts from raw LLM output."""
    if "```" in content:
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]

    parsed = json.loads(content.strip())

    if isinstance(parsed, dict):
        return parsed.get("data", parsed.get("recommendations", [parsed]))
    if isinstance(parsed, list):
        return parsed
    return []


def _safe_float(value, default=None) -> float | None:
    """Coerce a value to float, returning default on failure."""
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def _normalize_confidence(raw) -> float:
    """Normalize confidence to 0.0-1.0 range from various LLM formats."""
    try:
        value = float(str(raw).strip("%"))
        return value / 100 if value > 1 else value
    except (ValueError, TypeError):
        return 0.0


def _build_recommendation(raw: dict) -> Recommendation:
    """Build a Recommendation model from a raw LLM dict."""
    return Recommendation(
        symbol=raw.get("symbol", ""),
        name=raw.get("name", ""),
        action=str(raw.get("action", "HOLD")).upper(),
        rationale=raw.get("rationale", ""),
        confidence=_normalize_confidence(raw.get("confidence", 0)),
        target_price=_safe_float(raw.get("target_price")),
        stop_loss=_safe_float(raw.get("stop_loss")),
    )


def _serialize_recommendation(rec: Recommendation) -> dict:
    return {
        "id": rec.id,
        "symbol": rec.symbol,
        "name": rec.name,
        "action": rec.action,
        "rationale": rec.rationale,
        "confidence": rec.confidence,
        "target_price": rec.target_price,
        "stop_loss": rec.stop_loss,
        "created_at": rec.created_at.isoformat() if rec.created_at else None,
    }


async def _gather_context(holdings: list[Holding]) -> tuple[str, str, str]:
    """Gather portfolio, market, and news context for the LLM prompt."""
    holdings_text = "\n".join(
        f"- {h.symbol} ({h.name}): {h.quantity} units @ ₹{h.avg_price:.2f} | {h.asset_type}"
        for h in holdings
    )

    try:
        news_items = await fetch_news(max_items=5)
        news_text = "\n".join(f"- {n['title']}" for n in news_items)
    except Exception:
        log.exception("Failed to fetch news for recommendations")
        news_text = "News unavailable."

    market_text = "Market indices unavailable."
    try:
        indices = await asyncio.to_thread(get_index_quotes)
        if indices:
            market_text = "\n".join(
                f"- {i['name']}: {i['value']} ({i['change_pct']:+.2f}%)"
                for i in indices
            )
    except Exception:
        log.exception("Failed to fetch market indices for recommendations")

    return holdings_text, market_text, news_text


@router.post("/generate")
async def generate_recommendations(db: AsyncSession = Depends(get_db)) -> list[dict]:
    result = await db.execute(select(Holding))
    holdings = result.scalars().all()
    if not holdings:
        raise HTTPException(
            status_code=400, detail="No holdings found. Import your portfolio first."
        )

    holdings_text, market_text, news_text = await _gather_context(holdings)

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

    content = response["content"]
    log.debug("Raw LLM recommendation response: %s", content[:1000])

    try:
        recs_data = _parse_llm_json(content)
    except (json.JSONDecodeError, IndexError):
        log.error("Failed to parse LLM recommendation response: %s", content[:500])
        raise HTTPException(
            status_code=500,
            detail="Failed to parse LLM response into recommendations.",
        )

    await db.execute(delete(Recommendation))
    recs = []
    for raw in recs_data:
        rec = _build_recommendation(raw)
        db.add(rec)
        recs.append(rec)
    await db.commit()

    log.info("Generated %d recommendations", len(recs))
    return [_serialize_recommendation(r) for r in recs]


@router.get("")
async def list_recommendations(db: AsyncSession = Depends(get_db)) -> list[dict]:
    result = await db.execute(
        select(Recommendation).order_by(Recommendation.created_at.desc())
    )
    return [_serialize_recommendation(r) for r in result.scalars().all()]
