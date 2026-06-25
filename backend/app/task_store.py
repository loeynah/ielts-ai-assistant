"""每日任务清单持久化"""
from __future__ import annotations

from app.db import get_conn

# admin 种子账号默认今日任务（新注册用户不写入，保持空白）
ADMIN_DEFAULT_TASKS = [
    ("listening", "精听真题 Section 2 一篇并记录错题"),
    ("reading", "完成 Passage 1 并在系统中调用 AI 解析长难句"),
    ("speaking", "完成 1 轮 Part 2 录音盲考（Topic: 描述一个有趣的网络用户）"),
    ("writing", "完成 1 篇 Task 2 大作文（题目：科技对教育的影响）"),
]


def get_tasks(username: str) -> list[dict]:
    conn = get_conn()
    try:
        rows = conn.execute(
            """
            SELECT id, category, content, done, pinned, source, sort_order
            FROM daily_tasks
            WHERE username = ?
            ORDER BY sort_order ASC, id ASC
            """,
            (username,),
        ).fetchall()
    finally:
        conn.close()
    return [
        {
            "id": row["id"],
            "category": row["category"],
            "content": row["content"],
            "done": bool(row["done"]),
            "pinned": bool(row["pinned"]),
            "source": row["source"],
        }
        for row in rows
    ]


def seed_admin_tasks(username: str) -> None:
    """仅为 admin 种子账号写入默认任务；新注册用户保持空列表"""
    if get_tasks(username):
        return
    tasks = [
        {
            "category": cat,
            "content": content,
            "done": False,
            "pinned": False,
            "source": "system",
        }
        for cat, content in ADMIN_DEFAULT_TASKS
    ]
    replace_tasks(username, tasks)


def replace_tasks(username: str, tasks: list[dict]) -> list[dict]:
    conn = get_conn()
    try:
        conn.execute("DELETE FROM daily_tasks WHERE username = ?", (username,))
        for idx, task in enumerate(tasks):
            conn.execute(
                """
                INSERT INTO daily_tasks (username, category, content, done, pinned, source, sort_order)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    username,
                    task.get("category") or "other",
                    task.get("content") or "",
                    1 if task.get("done") else 0,
                    1 if task.get("pinned") else 0,
                    task.get("source") or "system",
                    idx,
                ),
            )
        conn.commit()
    finally:
        conn.close()
    return get_tasks(username)
