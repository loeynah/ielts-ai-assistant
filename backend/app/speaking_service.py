from __future__ import annotations

import json

from app.grading_rules import apply_speaking_penalties, count_words, is_simple_speech
from app.llm_helper import llm_json_or_mock
from app.prompt_manager import speaking_exam_system, speaking_practice_system, user_payload
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
        "advice": [f"{label}：未获取有效口语回答，无法评分。请重新录音。"],
        "examiner_corrections": "",
        "polished_text": "",
    }


def _grade_from_transcript(transcript: str, question: str, part_label: str, duration: float = 0) -> dict:
    if not _is_valid_transcript(transcript, duration):
        return _empty_part_report(part_label)

    wc = count_words(transcript)
    if wc < 30:
        sub = {"FC": 3.5, "LR": 3.5, "GRA": 3.5, "P": 4.0}
        advice = [
            "【严厉警告】字数严重不足，无法评估真实语言能力。",
            "Part 3 回答至少 4-6 句，含例子与展开，目标 60+ 词。",
        ]
    elif is_simple_speech(transcript):
        sub = {"FC": 5.0, "LR": 5.0, "GRA": 5.0, "P": 5.0}
        advice = [
            "表达过于简单：词汇重复、句型单一，LR/GRA 不得高于 5.5。",
            "使用从句、连接词与更精准动词替换 good/nice/think。",
        ]
    else:
        base = 5.0 if wc < 50 else 5.5 if wc < 80 else 6.0
        sub = {"FC": base, "LR": base, "GRA": max(4.5, base - 0.5), "P": base}
        advice = [
            f"基于真实转写（约 {wc} 词）评估。",
            "建议增加具体例子、对比与因果展开以提升 FC。",
        ]

    sub, _, extra = apply_speaking_penalties(sub, transcript)
    advice = extra + advice

    return {
        "user_text": transcript.strip(),
        "sub_scores": sub,
        "advice": advice,
        "examiner_corrections": "（Mock）请补充从句与具体例子，避免重复 I think...",
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
    return "\n\n".join(texts), max_dur


def _merge_part_report(llm_part: dict, transcript: str, label: str, duration: float) -> dict:
    base = _grade_from_transcript(transcript, label, label, duration) if transcript else _empty_part_report(label)
    if not isinstance(llm_part, dict) or not transcript:
        return base

    sub = llm_part.get("sub_scores") or base["sub_scores"]
    sub, _, extra = apply_speaking_penalties(sub, transcript)

    advice = llm_part.get("advice") or base["advice"]
    if isinstance(advice, str):
        advice = [advice]
    advice = extra + list(advice)

    corrections = llm_part.get("examiner_corrections") or base.get("examiner_corrections", "")
    if corrections and isinstance(corrections, str) and corrections not in str(advice):
        advice.insert(0, f"【考官纠错】{corrections[:500]}")

    return {
        "user_text": transcript.strip(),
        "sub_scores": sub,
        "advice": advice[:6],
        "examiner_corrections": corrections,
        "polished_text": llm_part.get("polished_text") or base.get("polished_text", ""),
    }


def _sanitize_exam_result(result: dict, payload: dict) -> dict:
    parts: dict = {}
    labels = {"part1": "Part 1", "part2": "Part 2", "part3": "Part 3"}
    llm_parts = result.get("parts") if isinstance(result.get("parts"), dict) else {}

    for key, single in [("part1", False), ("part2", True), ("part3", False)]:
        items = _part_items(payload, key, single)
        merged, dur = _merged_transcript(items)
        label = labels[key]
        llm_part = llm_parts.get(key) if isinstance(llm_parts, dict) else {}
        parts[key] = _merge_part_report(llm_part, merged, label, dur) if merged else _empty_part_report(label)

    valid_parts = [p for p in parts.values() if _is_valid_transcript(p.get("user_text", ""))]

    if not valid_parts:
        overall = 0.0
        sub = {"FC": 0, "LR": 0, "GRA": 0, "P": 0}
        advice = "本次考试未检测到有效口语回答，无法给出真实评分。请重新完成录音后再交卷。"
    else:
        sub = {
            dim: round_ielts_band(sum(p["sub_scores"][dim] for p in valid_parts) / len(valid_parts))
            for dim in ("FC", "LR", "GRA", "P")
        }
        all_text = " ".join(p.get("user_text", "") for p in valid_parts)
        overall = round_ielts_band(sum(sub.values()) / 4)
        sub, overall, extra = apply_speaking_penalties(sub, all_text, overall=overall)
        advice = result.get("general_advice") or "评分基于真实 STT 转写，已执行严厉官方标准。"
        if extra:
            advice = extra[0] + " " + str(advice)

    return {
        "overall_score": overall if valid_parts else 0.0,
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
        {"role": "system", "content": speaking_exam_system()},
        {"role": "user", "content": user_payload(exam=payload)},
    ]

    def mock_fn():
        return _build_exam_from_payload(payload)

    try:
        result = await llm_json_or_mock(messages, mock_fn)
    except Exception:
        result = mock_fn()

    return _sanitize_exam_result(result, payload)


def _normalize_sub_scores(raw: dict, fallback: float) -> dict:
    sub = raw.get("sub_scores") if isinstance(raw.get("sub_scores"), dict) else {}
    aliases = {
        "FC": ("fc", "fluency", "fluency_coherence"),
        "LR": ("lr", "lexical", "lexical_resource"),
        "GRA": ("gra", "grammar", "grammatical_range"),
        "P": ("p", "pronunciation"),
    }
    out: dict = {}
    for key, alts in aliases.items():
        val = sub.get(key)
        if val is None:
            for a in alts:
                if a in sub:
                    val = sub[a]
                    break
        out[key] = float(val if val is not None else fallback)
    return out


def _normalize_corrections(raw) -> list[dict]:
    corr = raw.get("examiner_corrections")
    if isinstance(corr, list):
        items = []
        for c in corr:
            if isinstance(c, dict) and (c.get("original") or c.get("corrected") or c.get("reason")):
                items.append(
                    {
                        "original": c.get("original", ""),
                        "corrected": c.get("corrected", ""),
                        "reason": c.get("reason", ""),
                    }
                )
        return items
    if isinstance(corr, str) and corr.strip():
        return [{"original": "", "corrected": "", "reason": corr.strip()}]
    return []


def _sanitize_practice_result(result: dict, transcript: str) -> dict:
    base = _grade_from_transcript(transcript, "", "练习", 0)
    fallback = float(
        result.get("overall_score")
        or result.get("score")
        or base["sub_scores"]["FC"]
    )
    sub = _normalize_sub_scores(result, fallback)
    overall = float(result.get("overall_score") or result.get("score") or fallback)
    sub, overall, extra = apply_speaking_penalties(sub, transcript, overall=overall)

    corrections = _normalize_corrections(result)
    if not corrections and base.get("examiner_corrections"):
        corrections = _normalize_corrections({"examiner_corrections": base["examiner_corrections"]})

    advice = result.get("advice") or ""
    if isinstance(advice, list):
        advice = " ".join(str(a) for a in advice)
    if extra:
        advice = extra[0] + (" " + advice if advice else "")

    polished = result.get("polished_text") or base.get("polished_text") or ""

    return {
        "overall_score": overall,
        "score": overall,
        "sub_scores": sub,
        "examiner_corrections": corrections,
        "polished_text": polished,
        "advice": advice,
        "vocab_upgrades": result.get("vocab_upgrades") or [],
        "transcript": transcript.strip(),
    }


async def grade_speaking_practice(question: str, transcript: str, duration: float = 0) -> dict:
    empty = {
        "overall_score": 0,
        "score": 0,
        "sub_scores": {"FC": 0, "LR": 0, "GRA": 0, "P": 0},
        "advice": "未检测到有效回答（录音过短或转写为空）。请重新录音或手动输入完整英文回答。",
        "examiner_corrections": [],
        "polished_text": "",
        "vocab_upgrades": [],
        "transcript": transcript or "",
    }
    if not _is_valid_transcript(transcript, duration):
        return empty

    messages = [
        {"role": "system", "content": speaking_practice_system()},
        {
            "role": "user",
            "content": user_payload(question=question, transcript=transcript, duration=duration),
        },
    ]

    def mock_fn():
        rep = _grade_from_transcript(transcript, question, "练习", duration)
        sub = rep["sub_scores"]
        overall = round_ielts_band(sub["FC"])
        return _sanitize_practice_result(
            {
                "sub_scores": sub,
                "overall_score": overall,
                "advice": rep["advice"][0] if rep["advice"] else "",
                "examiner_corrections": [
                    {
                        "original": transcript.split(".")[0] if "." in transcript else transcript[:80],
                        "corrected": "（示范）请使用从句与更精准动词展开论述。",
                        "reason": "句型单一 / 词汇重复，影响 GRA 与 LR。",
                    }
                ],
                "polished_text": rep.get("polished_text", ""),
            },
            transcript,
        )

    try:
        result = await llm_json_or_mock(messages, mock_fn)
    except Exception:
        result = mock_fn()

    if not _is_valid_transcript(transcript, duration):
        return empty

    return _sanitize_practice_result(result, transcript)
