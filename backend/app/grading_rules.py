from __future__ import annotations

import re

from app.score_utils import round_ielts_band


def count_words(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9']+", text or ""))


def objective_is_correct(user: str, correct: str) -> bool:
    u = (user or "").strip().lower()
    c = (correct or "").strip().lower()
    if not u or u in ("—", "-", "未作答"):
        return False
    return u == c


def is_simple_speech(transcript: str) -> bool:
    words = re.findall(r"[A-Za-z']+", (transcript or "").lower())
    if len(words) < 30:
        return True
    if not words:
        return True
    unique_ratio = len(set(words)) / len(words)
    avg_len = sum(len(w) for w in words) / len(words)
    simple_markers = sum(
        1
        for w in words
        if w in {"good", "bad", "nice", "like", "think", "very", "thing", "people", "because"}
    )
    return unique_ratio < 0.45 or avg_len < 4.2 or simple_markers / len(words) > 0.22


def apply_speaking_penalties(
    sub_scores: dict,
    transcript: str,
    *,
    overall: float | None = None,
) -> tuple[dict, float, list[str]]:
    sub = {k: float(sub_scores.get(k, 0)) for k in ("FC", "LR", "GRA", "P")}
    extra: list[str] = []
    wc = count_words(transcript)

    if wc < 30:
        sub["FC"] = min(sub["FC"], 3.5)
        sub["LR"] = min(sub["LR"], 3.5)
        sub["GRA"] = min(sub["GRA"], 3.5)
        cap = 3.5
        extra.append("【严厉警告】字数严重不足（低于 30 词），无法评估真实语言能力；流利度、词汇与语法分已熔断。")
        overall = min(overall if overall is not None else cap, cap)
    elif is_simple_speech(transcript):
        sub["LR"] = min(sub["LR"], 5.5)
        sub["GRA"] = min(sub["GRA"], 5.5)
        extra.append("表达过于简单：词汇与语法多样性不足，LR/GRA 不得高于 5.5。")

    for k in sub:
        sub[k] = round_ielts_band(sub[k])
    if overall is None:
        overall = round_ielts_band(sum(sub.values()) / 4)
    else:
        overall = round_ielts_band(overall)
    return sub, overall, extra


def apply_writing_penalties(
    task_type: str,
    essay_text: str,
    sub_scores: dict,
    overall: float,
) -> tuple[dict, float, list[str]]:
    sub = {k: float(sub_scores.get(k, 0)) for k in ("TR_TA", "CC", "LR", "GRA")}
    extra: list[str] = []
    wc = count_words(essay_text)
    tt = (task_type or "task2").lower()

    if tt == "task1":
        if wc < 50:
            sub["TR_TA"] = min(sub["TR_TA"], 3.0)
            overall = min(overall, 4.0)
            sub["CC"] = min(sub["CC"], sub["TR_TA"])
            sub["GRA"] = min(sub["GRA"], sub["TR_TA"])
            extra.append("Task 1 字数低于 50 词：TR/TA 锁定 3 分，总分不得超过 4.0。")
        elif wc < 100:
            sub["TR_TA"] = min(sub["TR_TA"], 4.0)
            sub["CC"] = min(sub["CC"], min(sub["TR_TA"] + 0.5, 5.0))
            sub["GRA"] = min(sub["GRA"], min(sub["TR_TA"] + 0.5, 5.0))
            extra.append("Task 1 字数低于 100 词：TR/TA 上限 4 分，CC/GRA 连带下调。")
    else:
        if wc < 80:
            sub["TR_TA"] = min(sub["TR_TA"], 3.0)
            sub["CC"] = min(sub["CC"], 4.0)
            sub["GRA"] = min(sub["GRA"], 4.0)
            extra.append("Task 2 字数低于 80 词：TR 锁定 3 分，结构分连带处罚。")
        elif wc < 180:
            sub["TR_TA"] = min(sub["TR_TA"], 4.0)
            sub["CC"] = min(sub["CC"], min(sub["TR_TA"] + 0.5, 5.5))
            sub["GRA"] = min(sub["GRA"], min(sub["TR_TA"] + 0.5, 5.5))
            extra.append("Task 2 字数低于 180 词：TR 上限 4 分，CC/GRA 不得虚高。")

    for k in sub:
        sub[k] = round(min(9.0, sub[k]) * 2) / 2 if k == "TR_TA" else round_ielts_band(sub[k])
    overall = round(min(9.0, overall) * 2) / 2
    return sub, overall, extra
