"""SQLite 用户画像 + 批改通知 + 会话"""
from __future__ import annotations

import json
import uuid
from datetime import date, datetime, timezone

from app.config import ADMIN_PASSWORD, ADMIN_USERNAME, ADMIN_USER_PROFILE, BLANK_USER_PROFILE
from app.db import get_conn, init_db
from app.task_store import seed_admin_tasks
from app.password_utils import hash_password, verify_password
from app.score_utils import round_ielts_band


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _inbox_time_label(created_at: str) -> str:
    try:
        dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        delta = datetime.now(timezone.utc) - dt.astimezone(timezone.utc)
        mins = int(delta.total_seconds() / 60)
        if mins < 1:
            return "刚刚"
        if mins < 60:
            return f"{mins} 分钟前"
        hours = mins // 60
        if hours < 24:
            return f"{hours} 小时前"
        return f"{delta.days} 天前"
    except Exception:
        return "刚刚"


def _optional_band(val) -> float | None:
    if val is None or val < 0:
        return None
    return round_ielts_band(val)


def _row_to_profile(row, inbox_rows) -> dict:
    inbox = [
        {
            "id": item["id"],
            "module": item["module"],
            "icon": item["icon"] or "✨",
            "title": item["title"],
            "meta": item["meta"] or "",
            "time": _inbox_time_label(item["created_at"]),
            "created_at": item["created_at"],
        }
        for item in inbox_rows
    ]
    exam_date = (row["exam_date"] or "").strip() or None
    return {
        "username": row["username"],
        "overall_score": _optional_band(row["overall_score"]),
        "target_score": _optional_band(row["target_score"]),
        "exam_date": exam_date,
        "skill_scores": {
            "listening": _optional_band(row["skill_listening"]),
            "reading": _optional_band(row["skill_reading"]),
            "speaking": _optional_band(row["skill_speaking"]),
            "writing": _optional_band(row["skill_writing"]),
        },
        "inbox": inbox,
    }


def _fetch_inbox(conn, username: str, limit: int = 20) -> list:
    cur = conn.execute(
        """
        SELECT id, module, icon, title, meta, created_at
        FROM inbox_items
        WHERE username = ?
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (username, limit),
    )
    return cur.fetchall()


def _get_user_row(conn, username: str):
    return conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()


def _welcome_inbox(conn, username: str, *, blank: bool = False) -> None:
    push_inbox(
        username,
        module="writing",
        title="欢迎加入雅思智能备考助手",
        meta="与 AI 助手对话，告诉我你的目标分数与考试时间" if blank else "目标 7.0 · 四科均衡起步",
        conn=conn,
    )


def seed_admin_user() -> None:
    """首次启动写入 .env 中的 admin 账号"""
    conn = get_conn()
    try:
        if _get_user_row(conn, ADMIN_USERNAME):
            return
        salt, pwd_hash = hash_password(ADMIN_PASSWORD)
        profile = ADMIN_USER_PROFILE
        conn.execute(
            """
            INSERT INTO users (
                username, password_hash, salt,
                overall_score, target_score, exam_date,
                skill_listening, skill_reading, skill_speaking, skill_writing,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ADMIN_USERNAME,
                pwd_hash,
                salt,
                profile["overall_score"],
                profile["target_score"],
                profile["exam_date"],
                profile["skill_scores"]["listening"],
                profile["skill_scores"]["reading"],
                profile["skill_scores"]["speaking"],
                profile["skill_scores"]["writing"],
                _now_iso(),
            ),
        )
        _welcome_inbox(conn, username=ADMIN_USERNAME)
        seed_admin_tasks(ADMIN_USERNAME)
        conn.commit()
    finally:
        conn.close()


def bootstrap_storage() -> None:
    init_db()
    seed_admin_user()


def register_user(username: str, password: str) -> dict:
    username = username.strip()
    if len(username) < 3 or len(username) > 32:
        raise ValueError("用户名长度需 3–32 个字符")
    if len(password) < 6:
        raise ValueError("密码至少 6 位")
    if _get_user_row(get_conn(), username):
        raise ValueError("用户名已存在")

    conn = get_conn()
    try:
        salt, pwd_hash = hash_password(password)
        profile = BLANK_USER_PROFILE
        conn.execute(
            """
            INSERT INTO users (
                username, password_hash, salt,
                overall_score, target_score, exam_date,
                skill_listening, skill_reading, skill_speaking, skill_writing,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                username,
                pwd_hash,
                salt,
                profile["overall_score"],
                profile["target_score"],
                profile["exam_date"],
                profile["skill_scores"]["listening"],
                profile["skill_scores"]["reading"],
                profile["skill_scores"]["speaking"],
                profile["skill_scores"]["writing"],
                _now_iso(),
            ),
        )
        _welcome_inbox(conn, username=username, blank=True)
        conn.commit()
    finally:
        conn.close()
    return get_user(username)


def verify_user_password(username: str, password: str) -> bool:
    conn = get_conn()
    try:
        row = _get_user_row(conn, username)
        if not row:
            return False
        return verify_password(password, row["salt"], row["password_hash"])
    finally:
        conn.close()


def init_user(username: str) -> dict:
    """兼容旧调用 — 若用户不存在则创建（无密码，仅供内部）"""
    conn = get_conn()
    try:
        if _get_user_row(conn, username):
            return get_user(username)
    finally:
        conn.close()
    salt, pwd_hash = hash_password(str(uuid.uuid4()))
    conn = get_conn()
    try:
        profile = BLANK_USER_PROFILE
        conn.execute(
            """
            INSERT INTO users (
                username, password_hash, salt,
                overall_score, target_score, exam_date,
                skill_listening, skill_reading, skill_speaking, skill_writing,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                username,
                pwd_hash,
                salt,
                profile["overall_score"],
                profile["target_score"],
                profile["exam_date"],
                profile["skill_scores"]["listening"],
                profile["skill_scores"]["reading"],
                profile["skill_scores"]["speaking"],
                profile["skill_scores"]["writing"],
                _now_iso(),
            ),
        )
        _welcome_inbox(conn, username=username, blank=True)
        conn.commit()
    finally:
        conn.close()
    return get_user(username)


def create_session(username: str) -> str:
    conn = get_conn()
    try:
        if not _get_user_row(conn, username):
            init_user(username)
        token = str(uuid.uuid4())
        conn.execute(
            "INSERT INTO sessions (token, username, created_at) VALUES (?, ?, ?)",
            (token, username, _now_iso()),
        )
        conn.commit()
        return token
    finally:
        conn.close()


def get_username_by_token(token: str) -> str | None:
    conn = get_conn()
    try:
        row = conn.execute("SELECT username FROM sessions WHERE token = ?", (token,)).fetchone()
        return row["username"] if row else None
    finally:
        conn.close()


def get_user(username: str) -> dict | None:
    conn = get_conn()
    try:
        row = _get_user_row(conn, username)
        if not row:
            return None
        inbox = _fetch_inbox(conn, username)
        return _row_to_profile(row, inbox)
    finally:
        conn.close()


def get_user_by_token(token: str) -> dict | None:
    username = get_username_by_token(token)
    if not username:
        return None
    return get_user(username)


def update_skill_score(username: str, module: str, score: float) -> dict:
    conn = get_conn()
    try:
        row = _get_user_row(conn, username)
        if not row:
            init_user(username)
            row = _get_user_row(conn, username)
        col = {
            "listening": "skill_listening",
            "reading": "skill_reading",
            "speaking": "skill_speaking",
            "writing": "skill_writing",
        }.get(module)
        if not col:
            return get_user(username)
        band = round_ielts_band(score)
        conn.execute(f"UPDATE users SET {col} = ? WHERE username = ?", (band, username))
        row = _get_user_row(conn, username)
        skills = [
            row["skill_listening"],
            row["skill_reading"],
            row["skill_speaking"],
            row["skill_writing"],
        ]
        valid = [s for s in skills if s is not None and s >= 0]
        overall = round_ielts_band(sum(valid) / len(valid)) if valid else -1
        conn.execute("UPDATE users SET overall_score = ? WHERE username = ?", (overall, username))
        conn.commit()
    finally:
        conn.close()
    return get_user(username)


def update_profile(
    username: str,
    *,
    exam_date: str | None = None,
    target_score: float | None = None,
) -> dict:
    conn = get_conn()
    try:
        if not _get_user_row(conn, username):
            init_user(username)
        if exam_date is not None:
            if exam_date == "":
                conn.execute("UPDATE users SET exam_date = ? WHERE username = ?", ("", username))
            else:
                try:
                    date.fromisoformat(exam_date)
                except ValueError as exc:
                    raise ValueError("exam_date 格式须为 YYYY-MM-DD") from exc
                conn.execute("UPDATE users SET exam_date = ? WHERE username = ?", (exam_date, username))
        if target_score is not None:
            conn.execute(
                "UPDATE users SET target_score = ? WHERE username = ?",
                (round_ielts_band(target_score), username),
            )
        conn.commit()
    finally:
        conn.close()
    return get_user(username)


def push_inbox(
    username: str,
    *,
    module: str,
    title: str,
    meta: str,
    conn=None,
) -> dict:
    own_conn = conn is None
    if own_conn:
        conn = get_conn()
    try:
        if not _get_user_row(conn, username):
            init_user(username)
        item_id = str(uuid.uuid4())
        icon = {"listening": "🎧", "reading": "📖", "speaking": "🎤", "writing": "📝"}.get(module, "✨")
        created = _now_iso()
        conn.execute(
            """
            INSERT INTO inbox_items (id, username, module, icon, title, meta, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (item_id, username, module, icon, title, meta, created),
        )
        if own_conn:
            conn.commit()
        return {
            "id": item_id,
            "module": module,
            "icon": icon,
            "title": title,
            "meta": meta,
            "time": "刚刚",
            "created_at": created,
        }
    finally:
        if own_conn:
            conn.close()
