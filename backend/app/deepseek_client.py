"""DeepSeek-V3 统一调用层（失败时由业务层降级 Mock）"""
from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from app.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL

logger = logging.getLogger(__name__)


async def chat_completion(
    messages: list[dict[str, str]],
    *,
    temperature: float = 0.4,
    json_mode: bool = False,
) -> str:
    if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == "123":
        raise RuntimeError("未配置 DEEPSEEK_API_KEY，请在 backend/.env 中设置")

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }
    payload: dict[str, Any] = {
        "model": DEEPSEEK_MODEL,
        "messages": messages,
        "temperature": temperature,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    async with httpx.AsyncClient(timeout=90.0) as client:
        res = await client.post(
            f"{DEEPSEEK_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
        )
        if not res.is_success:
            detail = res.text[:300]
            logger.error(
                "LLM API %s model=%s -> %s %s",
                DEEPSEEK_BASE_URL,
                DEEPSEEK_MODEL,
                res.status_code,
                detail,
            )
            raise RuntimeError(f"LLM 请求失败 ({res.status_code}): {detail}")
        data = res.json()
        return data["choices"][0]["message"]["content"]


async def chat_json(messages: list[dict[str, str]]) -> dict[str, Any]:
    raw = await chat_completion(messages, json_mode=True)
    return json.loads(raw)
