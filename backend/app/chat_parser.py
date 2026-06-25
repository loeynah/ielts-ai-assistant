"""解析 LLM 回复中的 META / TODAY_TASKS 结构化块"""
from __future__ import annotations

import re
from typing import Any

BLOCK_RE = re.compile(r"\[(META|TODAY_TASKS)\](.*?)\[/\1\]", re.DOTALL)


def _parse_meta(block: str) -> dict[str, Any]:
    meta: dict[str, Any] = {}
    for line in block.strip().splitlines():
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        key = key.strip().lower()
        val = val.strip()
        if key == "exam_date":
            meta["exam_date"] = val
        elif key == "target_score":
            try:
                meta["target_score"] = float(val)
            except ValueError:
                pass
    return meta


def _parse_tasks(block: str) -> list[dict[str, str]]:
    tasks: list[dict[str, str]] = []
    valid = {"listening", "reading", "speaking", "writing", "other"}
    for line in block.strip().splitlines():
        line = line.strip()
        if not line or "|" not in line:
            continue
        cat, content = line.split("|", 1)
        cat = cat.strip().lower()
        content = content.strip()
        if not content:
            continue
        if cat not in valid:
            cat = "other"
        tasks.append({"category": cat, "content": content})
    return tasks


def parse_chat_response(raw: str) -> dict[str, Any]:
    meta: dict[str, Any] = {}
    today_tasks: list[dict[str, str]] = []

    for match in BLOCK_RE.finditer(raw):
        tag, body = match.group(1), match.group(2)
        if tag == "META":
            meta.update(_parse_meta(body))
        elif tag == "TODAY_TASKS":
            today_tasks.extend(_parse_tasks(body))

    content = BLOCK_RE.sub("", raw).strip()
    return {
        "content": content,
        "exam_date": meta.get("exam_date"),
        "target_score": meta.get("target_score"),
        "today_tasks": today_tasks,
    }
