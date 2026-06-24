from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from app.deepseek_client import chat_json

logger = logging.getLogger(__name__)

T = TypeVar("T")


async def llm_json_or_mock(
    messages: list[dict[str, str]],
    mock_fn: Callable[[], T],
    *,
    source_key: str = "source",
    llm_source: str = "deepseek",
    mock_source: str = "backend-mock",
    temperature: float = 0.2,
) -> T:
    try:
        from app.deepseek_client import chat_completion
        import json as _json

        raw = await chat_completion(messages, temperature=temperature, json_mode=True)
        data = _json.loads(raw)
        if isinstance(data, dict) and source_key:
            data[source_key] = llm_source
        return data  # type: ignore[return-value]
    except Exception as exc:
        logger.warning("DeepSeek unavailable, fallback to mock: %s", exc)
        result = mock_fn()
        if isinstance(result, dict) and source_key:
            result[source_key] = mock_source
        return result
