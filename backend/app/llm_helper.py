"""LLM 调用统一降级：DeepSeek 失败时回退业务 Mock"""
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
) -> T:
    try:
        data = await chat_json(messages)
        if isinstance(data, dict) and source_key:
            data[source_key] = llm_source
        return data  # type: ignore[return-value]
    except Exception as exc:
        logger.warning("DeepSeek unavailable, fallback to mock: %s", exc)
        result = mock_fn()
        if isinstance(result, dict) and source_key:
            result[source_key] = mock_source
        return result
