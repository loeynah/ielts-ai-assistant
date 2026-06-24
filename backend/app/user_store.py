"""内存用户画像 + 批改通知（生产可换数据库）"""
from __future__ import annotations

import copy
import uuid
from datetime import datetime, timezone

from app.config import DEFAULT_USER_PROFILE
from app.score_utils import round_ielts_band

_sessions: dict[str, str] = {}
_users: dict[str, dict] = {}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def init_user(username: str) -> dict:
    profile = copy.deepcopy(DEFAULT_USER_PROFILE)
    profile["username"] = username
    profile["inbox"] = [
        {
            "id": str(uuid.uuid4()),
            "module": "writing",
            "title": "欢迎加入雅思智能备考助手",
            "meta": "目标 7.0 · 四科均衡起步",
            "time": "刚刚",
            "created_at": _now_iso(),
        }
    ]
    _users[username] = profile
    return profile


def create_session(username: str) -> str:
    token = str(uuid.uuid4())
    _sessions[token] = username
    if username not in _users:
        init_user(username)
    return token


def get_username_by_token(token: str) -> str | None:
    return _sessions.get(token)


def get_user(username: str) -> dict | None:
    return _users.get(username)


def get_user_by_token(token: str) -> dict | None:
    username = get_username_by_token(token)
    if not username:
        return None
    return get_user(username)


def update_skill_score(username: str, module: str, score: float) -> dict:
    user = get_user(username) or init_user(username)
    user["skill_scores"][module] = round_ielts_band(score)
    scores = user["skill_scores"].values()
    user["overall_score"] = round_ielts_band(sum(scores) / len(scores))
    return user


def update_profile(username: str, *, exam_date: str | None = None, target_score: float | None = None) -> dict:
    user = get_user(username) or init_user(username)
    if exam_date is not None:
        user["exam_date"] = exam_date
    if target_score is not None:
        user["target_score"] = round_ielts_band(target_score)
    return user


def push_inbox(
    username: str,
    *,
    module: str,
    title: str,
    meta: str,
) -> dict:
    user = get_user(username) or init_user(username)
    item = {
        "id": str(uuid.uuid4()),
        "module": module,
        "icon": {"listening": "🎧", "reading": "📖", "speaking": "🎤", "writing": "📝"}.get(
            module, "✨"
        ),
        "title": title,
        "meta": meta,
        "time": "刚刚",
        "created_at": _now_iso(),
    }
    user["inbox"].insert(0, item)
    user["inbox"] = user["inbox"][:20]
    return item
