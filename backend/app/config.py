"""全局配置 — DeepSeek-V3 与鉴权占位"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# 自动加载 backend/.env（无需每次在终端手动 export）
_ENV_FILE = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(_ENV_FILE)

DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "123")
# 官方 DeepSeek API 模型名是 deepseek-chat（不是 deepseek-ai/DeepSeek-V3）
DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "123456")

DEFAULT_USER_PROFILE = {
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


def llm_config_status() -> dict:
    key = DEEPSEEK_API_KEY or ""
    configured = bool(key) and key != "123"
    return {
        "configured": configured,
        "base_url": DEEPSEEK_BASE_URL,
        "model": DEEPSEEK_MODEL,
        "key_preview": f"{key[:6]}...{key[-4:]}" if len(key) > 12 else ("(未设置)" if not configured else "(已设置)"),
    }
