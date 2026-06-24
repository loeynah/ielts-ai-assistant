"""全局配置 — LLM（默认 SiliconFlow DeepSeek）与鉴权"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# 自动加载 backend/.env（无需每次在终端手动 export）
_ENV_FILE = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(_ENV_FILE)

# 默认走 SiliconFlow OpenAI 兼容接口；Key 须在 .env 中自行填写
DEEPSEEK_API_KEY: str = (os.getenv("DEEPSEEK_API_KEY") or "").strip()
DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.siliconflow.cn/v1").rstrip("/")
DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-ai/DeepSeek-V3")

_ADMIN_PLACEHOLDERS = frozenset({"123", "你的deepseek密钥", "你的DeepSeek密钥"})

ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "123456")

# admin 种子账号：考试 6/25、目标 7.0、四科 6.0
ADMIN_USER_PROFILE = {
    "username": "admin",
    "overall_score": 6.0,
    "target_score": 7.0,
    "exam_date": "2026-06-25",
    "skill_scores": {
        "listening": 6.0,
        "reading": 6.0,
        "speaking": 6.0,
        "writing": 6.0,
    },
}

# 新注册用户：无考试时间、无目标分、无能力诊断分（-1 表示未设定）
BLANK_USER_PROFILE = {
    "overall_score": -1,
    "target_score": -1,
    "exam_date": "",
    "skill_scores": {
        "listening": -1,
        "reading": -1,
        "speaking": -1,
        "writing": -1,
    },
}

# 兼容旧引用
DEFAULT_USER_PROFILE = ADMIN_USER_PROFILE


def is_llm_key_configured(key: str | None = None) -> bool:
    """Key 须为非空 ASCII 字符串（SiliconFlow / DeepSeek 官方 Key 均为 sk- 等英文）"""
    k = (key if key is not None else DEEPSEEK_API_KEY).strip()
    if not k or k.lower() in _ADMIN_PLACEHOLDERS:
        return False
    try:
        k.encode("ascii")
    except UnicodeEncodeError:
        return False
    return len(k) >= 8


def llm_config_status() -> dict:
    key = DEEPSEEK_API_KEY
    configured = is_llm_key_configured(key)
    provider = "SiliconFlow" if "siliconflow" in DEEPSEEK_BASE_URL.lower() else "DeepSeek"
    return {
        "configured": configured,
        "provider": provider,
        "base_url": DEEPSEEK_BASE_URL,
        "model": DEEPSEEK_MODEL,
        "key_preview": f"{key[:6]}...{key[-4:]}" if configured and len(key) > 12 else "(未设置)",
    }
