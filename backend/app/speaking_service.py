"""口语批改 — 仅基于真实 STT 转写评分，禁止编造"""
from __future__ import annotations

import json

from app.llm_helper import llm_json_or_mock
from app.score_utils import round_ielts_band

MIN_TRANSCRIPT_CHARS = 8
MIN_DURATION_SEC = 2.0


def _is_valid_transcript(text: str, duration: float = 0) -> bool:
    t = (text or "").strip()
    if not t or t in ("—", "-", "未作答"):
        return False
    if "未检测到有效语音" in t or "无转写文本" in t:
        return False
    if duration > 0 and duration < MIN_DURATION_SEC:
        return False
    return len(t) >= MIN_TRANSCRIPT_CHARS


def _empty_part_report(label: str) -> dict:
    return {
        "user_text": "（未检测到有效语音 / 无转写文本）",
        "sub_scores": {"FC": 0, "LR": 0, "GRA": 0, "P": 0},
        "advice": [f"{label}：未获取到你的有效口语回答，无法评分。请重新录音并确保麦克风权限已开启。"],
        "polished_text": "",
    }


def _grade_from_transcript(transcript: str, question: str, part_label: str, duration: float = 0) -> dict:
    if not _is_valid_transcript(transcript, duration):
        return _empty_part_report(part_label)

    word_count = len(transcript.split())
    base = 4.0 if word_count < 8 else 5.0 if word_count < 20 else 5.5 if word_count < 40 else 6.0
    score = round_ielts_band(base)
    return {
        "user_text": transcript.strip(),
        "sub_scores": {"FC": score, "LR": score, "GRA": max(4.0, score - 0.5), "P": score},
        "advice": [
            f"基于你的真实回答（约 {word_count} 词）给出评估。",
            "建议围绕题目给出更具体的例子与细节展开。",
        ],
        "polished_text": "",
    }


def _part_items(payload: dict, key: str, single: bool = False) -> list[dict]:
    raw = payload.get(key)
    if single:
        return [raw] if isinstance(raw, dict) and raw else []
    return raw if isinstance(raw, list) else []


def _merged_transcript(items: list[dict]) -> tuple[str, float]:
    texts = []
    max_dur = 0.0
    for item in items:
        t = (item.get("transcript") or "").strip()
        d = float(item.get("duration") or 0)
        max_dur = max(max_dur, d)
        if _is_valid_transcript(t, d):
            q = item.get("question", "")
            texts.append(f"Q: {q}\nA: {t}" if q else t)
    merged = "\n\n".join(texts)
    return merged, max_dur


def _sanitize_exam_result(result: dict, payload: dict) -> dict:
    """用真实转写强制覆盖 LLM 结果，无转写则分数为 0"""
    parts: dict = {}
    labels = {"part1": "Part 1", "part2": "Part 2", "part3": "Part 3"}

    for key, single in [("part1", False), ("part2", True), ("part3", False)]:
        items = _part_items(payload, key, single)
        merged, dur = _merged_transcript(items)
        label = labels[key]
        if merged:
            parts[key] = _grade_from_transcript(merged, label, label, dur)
        else:
            parts[key] = _empty_part_report(label)

    valid_parts = [
        p for p in parts.values() if _is_valid_transcript(p.get("user_text", ""))
    ]

    if not valid_parts:
        overall = 0.0
        sub = {"FC": 0, "LR": 0, "GRA": 0, "P": 0}
        advice = "本次考试未检测到有效口语回答，无法给出真实评分。请重新完成录音后再交卷。"
    else:
        overall = round_ielts_band(
            sum(p["sub_scores"]["FC"] for p in valid_parts) / len(valid_parts)
        )
        sub = {
            dim: round_ielts_band(
                sum(p["sub_scores"][dim] for p in valid_parts) / len(valid_parts)
            )
            for dim in ("FC", "LR", "GRA", "P")
        }
        advice = result.get("general_advice") or "评分基于你的真实 STT 转写，建议加强论证深度与词汇多样性。"

    return {
        "overall_score": overall,
        "sub_scores": sub,
        "parts": parts,
        "general_advice": advice,
        "valid_answer_count": len(valid_parts),
    }


def _build_exam_from_payload(payload: dict) -> dict:
    return _sanitize_exam_result({}, payload)


async def grade_speaking_exam(payload: dict) -> dict:
    if not isinstance(payload, dict):
        payload = {}

    messages = [
        {
            "role": "system",
            "content": (
                "你是雅思口语考官。仅根据学生真实 STT 转写文本评分，禁止编造学生未说过的话。"
                "若某 Part 无有效转写，该 Part 分数为 0。"
                "输出 JSON 含 overall_score, sub_scores, parts, general_advice。"
                "分数 0-9，0.5 进制。建议用中文。"
            ),
        },
        {
            "role": "user",
            "content": json.dumps(payload, ensure_ascii=False),
        },
    ]

    def mock_fn():
        return _build_exam_from_payload(payload)

    try:
        result = await llm_json_or_mock(messages, mock_fn)
    except Exception:
        result = mock_fn()

    return _sanitize_exam_result(result, payload)


async def grade_speaking_practice(question: str, transcript: str, duration: float = 0) -> dict:
    if not _is_valid_transcript(transcript, duration):
        return {
            "score": 0,
            "advice": "未检测到有效回答（录音过短或转写为空）。请重新录音，或在文本框中手动输入至少一句完整英文回答后再提交。",
            "vocab_upgrades": [],
            "transcript": transcript or "",
        }

    messages = [
        {
            "role": "system",
            "content": (
                "你是雅思口语教练。仅根据学生真实转写文本评分，禁止编造内容。"
                '输出 JSON：{"score":6.0,"advice":"","vocab_upgrades":[{"original","upgrade"}]}'
                "。分数 0-9，0.5 进制。建议用中文。"
            ),
        },
        {
            "role": "user",
            "content": json.dumps(
                {"question": question, "transcript": transcript},
                ensure_ascii=False,
            ),
        },
    ]

    def mock_fn():
        rep = _grade_from_transcript(transcript, question, "练习", duration)
        return {
            "score": rep["sub_scores"]["FC"],
            "advice": rep["advice"][0] if rep["advice"] else "请继续练习。",
            "vocab_upgrades": [],
            "transcript": transcript,
        }

    try:
        result = await llm_json_or_mock(messages, mock_fn)
    except Exception:
        result = mock_fn()

    if not _is_valid_transcript(transcript, duration):
        return {
            "score": 0,
            "advice": "未检测到有效回答，无法评分。",
            "vocab_upgrades": [],
            "transcript": transcript or "",
        }

    result["transcript"] = transcript.strip()
    result["score"] = round_ielts_band(float(result.get("score", 0)))
    return result
