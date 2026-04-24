import logging
from collections.abc import AsyncGenerator

from openrouter import OpenRouter

from app.config import settings

log = logging.getLogger(__name__)

_client: OpenRouter | None = None


def get_client() -> OpenRouter:
    global _client
    if _client is None:
        _client = OpenRouter(api_key=settings.openrouter_api_key)
    return _client


async def chat_completion(
    messages: list[dict],
    model: str | None = None,
    temperature: float = 0.7,
    stream: bool = False,
):
    model = model or settings.default_model
    client = get_client()

    log.info("LLM request: model=%s, stream=%s, messages=%d", model, stream, len(messages))

    if stream:
        return _stream_response(client, messages, model, temperature)

    response = await client.chat.send_async(
        model=model,
        messages=messages,
        temperature=temperature,
        stream=False,
    )
    content = response.choices[0].message.content or ""
    log.info("LLM response received: %d chars", len(content))
    return {"role": "assistant", "content": content}


async def _stream_response(
    client: OpenRouter,
    messages: list[dict],
    model: str,
    temperature: float,
) -> AsyncGenerator[dict, None]:
    stream = await client.chat.send_async(
        model=model,
        messages=messages,
        temperature=temperature,
        stream=True,
    )
    async for chunk in stream:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta
        if delta and delta.content:
            yield {"text": delta.content}
    log.debug("LLM stream completed")
