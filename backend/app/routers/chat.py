import json
import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import ChatMessage, Holding
from app.prompts.system import SYSTEM_PROMPT
from app.services.llm import chat_completion
from app.services.news import fetch_news

log = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None
    stream: bool = True


def _format_holdings_context(holdings: list[Holding]) -> str:
    if not holdings:
        return "No portfolio data available. User has not imported holdings yet."
    lines = []
    for h in holdings:
        lines.append(
            f"- {h.symbol} ({h.name}): {h.quantity} units @ ₹{h.avg_price:.2f} avg | Type: {h.asset_type}"
        )
    return "\n".join(lines)


async def _build_context(db: AsyncSession) -> str:
    result = await db.execute(select(Holding))
    holdings = result.scalars().all()
    portfolio_ctx = _format_holdings_context(holdings)

    try:
        news = await fetch_news(max_items=5)
        news_ctx = "\n".join(f"- {n['title']} ({n['source']})" for n in news)
    except Exception:
        log.exception("Failed to fetch news for chat context")
        news_ctx = "News unavailable."

    return (
        f"## Portfolio\n{portfolio_ctx}\n\n"
        f"## Recent Market News\n{news_ctx}\n\n"
        f"Timestamp: {datetime.now(timezone.utc).isoformat()}"
    )


async def _get_conversation_history(
    db: AsyncSession, conversation_id: str, limit: int = 20
) -> list[dict]:
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.conversation_id == conversation_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
    )
    messages = list(reversed(result.scalars().all()))
    return [{"role": m.role, "content": m.content} for m in messages]


@router.post("")
async def chat(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    conversation_id = req.conversation_id or str(uuid.uuid4())
    context = await _build_context(db)

    system_msg = {"role": "system", "content": f"{SYSTEM_PROMPT}\n\n{context}"}
    history = await _get_conversation_history(db, conversation_id)
    messages = [system_msg, *history, {"role": "user", "content": req.message}]

    # Persist user message
    db.add(
        ChatMessage(
            conversation_id=conversation_id,
            role="user",
            content=req.message,
        )
    )
    await db.commit()

    if req.stream:
        return StreamingResponse(
            _stream_and_persist(messages, conversation_id, db),
            media_type="text/event-stream",
            headers={
                "X-Conversation-Id": conversation_id,
                "Cache-Control": "no-cache",
            },
        )

    response = await chat_completion(messages, stream=False)
    db.add(
        ChatMessage(
            conversation_id=conversation_id,
            role="assistant",
            content=response["content"],
        )
    )
    await db.commit()
    return {"conversation_id": conversation_id, "response": response["content"]}


async def _stream_and_persist(
    messages: list[dict], conversation_id: str, db: AsyncSession
):
    full_content = []
    generator = await chat_completion(messages, stream=True)
    async for chunk in generator:
        text = chunk.get("text", "")
        if text:
            full_content.append(text)
            yield f"data: {json.dumps({'text': text, 'conversation_id': conversation_id})}\n\n"

    assistant_content = "".join(full_content)
    if assistant_content:
        db.add(
            ChatMessage(
                conversation_id=conversation_id,
                role="assistant",
                content=assistant_content,
            )
        )
        await db.commit()

    yield f"data: {json.dumps({'done': True, 'conversation_id': conversation_id})}\n\n"


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str, db: AsyncSession = Depends(get_db)
) -> list[dict]:
    return await _get_conversation_history(db, conversation_id, limit=100)
