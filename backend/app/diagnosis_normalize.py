"""听/读诊断 LLM 输出归一化 — 动态题号字典 → items 数组 + 客观对错强制对齐"""
from __future__ import annotations

from app.diagnosis_items import display_num_for, ordered_question_ids
from app.grading_rules import objective_is_correct


def _normalize_answer(ans) -> tuple[str, str]:
    user = getattr(ans, "user_ans", None) or ans.get("user_ans", "")
    correct = getattr(ans, "correct_ans", None) or ans.get("correct_ans", "")
    return user, correct


def _parse_paraphrase_pairs(raw) -> list[dict]:
    if isinstance(raw, list):
        pairs = []
        for p in raw:
            if isinstance(p, dict):
                pairs.append(
                    {
                        "original": p.get("original", p.get("原文", "")),
                        "replacement": p.get("replacement", p.get("替换", p.get("upgrade", ""))),
                    }
                )
        return [p for p in pairs if p["original"] or p["replacement"]]
    if isinstance(raw, str) and raw.strip():
        pairs = []
        for line in raw.replace("；", "\n").split("\n"):
            line = line.strip()
            if not line:
                continue
            for sep in ("→", "->", "—", "-", "：", ":"):
                if sep in line:
                    a, b = line.split(sep, 1)
                    pairs.append({"original": a.strip(), "replacement": b.strip()})
                    break
            else:
                pairs.append({"original": line, "replacement": ""})
        return pairs
    return []


def _item_from_slice(num: str, slice_data: dict, qid: str, user: str, correct: str, mode: str) -> dict:
    is_correct = objective_is_correct(user, correct)
    status = (slice_data.get("status") or "").strip()
    if status in ("正确", "correct", "true"):
        pass  # still trust objective
    elif status in ("错误", "incorrect", "false"):
        pass

    analysis = (
        slice_data.get("analysis")
        or slice_data.get("error_analysis")
        or ("定位准确，同义替换识别到位。" if is_correct else f"错选「{user}」，正确答案为「{correct}」。")
    )
    suggestion = slice_data.get("suggestion") or slice_data.get("listening_tip") or slice_data.get("reading_tip") or ""
    paraphrase = slice_data.get("paraphrase") or slice_data.get("knowledge_point") or ""

    item = {
        "question_id": qid,
        "display_num": num,
        "label": num,
        "is_correct": is_correct,
        "correct_answer": slice_data.get("correct_answer") or correct,
        "error_analysis": analysis,
        "knowledge_point": paraphrase if isinstance(paraphrase, str) else "",
    }
    if mode == "listening":
        item["listening_tip"] = suggestion or ("保持精听节奏。" if is_correct else "1.0x 精听答案句前后 2 句，标注转折词。")
    else:
        item["reading_tip"] = suggestion or ("回读定位段落，标出转折与同义替换。" if not is_correct else "保持当前定位节奏。")
        item["paraphrase_pairs"] = _parse_paraphrase_pairs(
            slice_data.get("paraphrase_pairs") or paraphrase
        )
    return item


def normalize_diagnosis_result(
    result: dict,
    all_answers: dict,
    question_meta: list | None,
    *,
    mode: str,
) -> list[dict]:
    """将 LLM 返回的 items 数组或 {题号: {...}} 字典统一为前端 items 列表"""
    raw_items = result.get("items") or result.get("diagnosis") or result.get("questions") or {}
    by_num: dict[str, dict] = {}

    if isinstance(raw_items, dict):
        by_num = {str(k): v for k, v in raw_items.items() if isinstance(v, dict)}
    elif isinstance(raw_items, list):
        for it in raw_items:
            if not isinstance(it, dict):
                continue
            num = str(it.get("display_num") or it.get("label") or it.get("question_id", "")).lstrip("qQ")
            by_num[num] = it

    merged: list[dict] = []
    for qid in ordered_question_ids(all_answers, question_meta):
        user, correct = _normalize_answer(all_answers.get(qid) or {})
        num = display_num_for(qid, question_meta)
        slice_data = by_num.get(num) or by_num.get(qid) or by_num.get(str(qid)) or {}
        merged.append(_item_from_slice(num, slice_data, qid, user, correct, mode))
    return merged
