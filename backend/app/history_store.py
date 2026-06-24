from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from app.db import get_conn


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def save_practice_record(
    username: str,
    *,
    module: str,
    record_type: str,
    ref_id: str = "",
    title: str = "",
    overall_score: float | None,
    payload: dict,
    meta: dict | None = None,
) -> dict:
    record_id = str(uuid.uuid4())
    created = _now_iso()
    full_payload = dict(payload)
    if meta:
        full_payload["_meta"] = meta
    conn = get_conn()
    try:
        conn.execute(
            """
            INSERT INTO practice_records (
                id, username, module, record_type, ref_id, title,
                overall_score, payload_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record_id,
                username,
                module,
                record_type,
                ref_id or "",
                title or "",
                overall_score,
                json.dumps(full_payload, ensure_ascii=False),
                created,
            ),
        )
        conn.commit()
    finally:
        conn.close()
    return {"id": record_id, "timestamp": created, "created_at": created}


def list_practice_records(username: str, module: str, *, limit: int = 30) -> list[dict]:
    conn = get_conn()
    try:
        rows = conn.execute(
            """
            SELECT id, module, record_type, ref_id, title, overall_score, payload_json, created_at
            FROM practice_records
            WHERE username = ? AND module = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (username, module, limit),
        ).fetchall()
    finally:
        conn.close()

    out: list[dict] = []
    for row in rows:
        try:
            payload = json.loads(row["payload_json"])
        except json.JSONDecodeError:
            payload = {}
        meta = payload.pop("_meta", {}) if isinstance(payload, dict) else {}
        item = {
            "id": row["id"],
            "timestamp": row["created_at"],
            "module": row["module"],
            "record_type": row["record_type"],
            "ref_id": row["ref_id"],
            "title": row["title"],
            "overall_score": row["overall_score"],
            "payload": payload,
        }
        if module == "speaking":
            item.update(_format_speaking_record(row, payload, meta))
        elif module in ("listening", "reading"):
            item.update(_format_diagnose_record(row, payload, meta))
        elif module == "writing":
            item.update(_format_writing_record(row, payload, meta))
        out.append(item)
    return out


def _format_speaking_record(row, payload: dict, meta: dict) -> dict:
    sub = payload.get("sub_scores") or meta.get("sub_scores") or {}
    return {
        "exam_id": meta.get("exam_id") or row["ref_id"],
        "exam_title": meta.get("exam_title") or row["title"],
        "mode": meta.get("mode") or row["record_type"],
        "overall_score": payload.get("overall_score") or payload.get("score") or row["overall_score"],
        "sub_scores": sub,
        "rounds": meta.get("rounds"),
        "audio_count": meta.get("audio_count"),
        "grade": payload,
    }


def _format_diagnose_record(row, payload: dict, meta: dict) -> dict:
    items = payload.get("items") or []
    correct = sum(1 for i in items if i.get("is_correct"))
    total = len(items)
    return {
        "lesson_id": meta.get("lesson_id") or row["ref_id"],
        "exam_id": meta.get("exam_id") or row["ref_id"],
        "title": meta.get("title") or row["title"],
        "score": payload.get("updated_score") or row["overall_score"],
        "correct_count": correct,
        "total_count": total,
        "items": items,
        "diagnosis": payload,
    }


def _format_writing_record(row, payload: dict, meta: dict) -> dict:
    return {
        "task_id": meta.get("task_id") or row["ref_id"],
        "task_type": meta.get("task_type"),
        "overall_score": payload.get("overall_score") or row["overall_score"],
        "sub_scores": payload.get("sub_scores") or {},
        "report": payload,
    }
