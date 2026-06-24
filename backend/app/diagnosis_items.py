"""诊断 items 合并 — 保证与前端题号列表绝对同步"""
from __future__ import annotations


def _q_sort_key(qid: str) -> tuple:
    raw = str(qid).lower().lstrip("q")
    if raw.isdigit():
        return (0, int(raw))
    return (1, raw)


def _normalize_answer(ans) -> tuple[str, str]:
    user = getattr(ans, "user_ans", None) or ans.get("user_ans", "")
    correct = getattr(ans, "correct_ans", None) or ans.get("correct_ans", "")
    return user, correct


def ordered_question_ids(all_answers: dict, question_meta: list | None = None) -> list[str]:
    if question_meta:
        return [str(m.get("id", "")) for m in question_meta if m.get("id")]
    return sorted(all_answers.keys(), key=_q_sort_key)


def display_num_for(qid: str, question_meta: list | None) -> str:
    if question_meta:
        for m in question_meta:
            if str(m.get("id")) == str(qid):
                return str(m.get("num", qid)).lstrip("qQ")
    return str(qid).lstrip("qQ")


def ensure_diagnosis_items(
    items: list,
    all_answers: dict,
    question_meta: list | None,
    *,
    mode: str,
    mock_item_fn,
) -> list:
    by_id: dict[str, dict] = {}
    for item in items:
        qid = str(item.get("question_id", ""))
        if qid:
            by_id[qid] = item

    merged: list[dict] = []
    for qid in ordered_question_ids(all_answers, question_meta):
        ans = all_answers.get(qid) or {}
        user, correct = _normalize_answer(ans)
        num = display_num_for(qid, question_meta)
        if qid in by_id:
            item = dict(by_id[qid])
            item["question_id"] = qid
            item["display_num"] = num
            item["label"] = num
            merged.append(item)
        else:
            is_correct = user.strip().lower() == correct.strip().lower() and user.strip() not in ("", "—")
            merged.append(mock_item_fn(qid, user, correct, is_correct, num, mode))
    return merged
