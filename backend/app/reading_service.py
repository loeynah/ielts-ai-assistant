"""阅读切片诊断 + 随身助理 — 严厉判分 + 动态题号结构化 JSON"""
from __future__ import annotations

import json

from app.diagnosis_items import ensure_diagnosis_items
from app.diagnosis_normalize import normalize_diagnosis_result
from app.grading_rules import objective_is_correct
from app.llm_helper import llm_json_or_mock
from app.prompt_manager import reading_diagnosis_system, user_payload


def _normalize_answer(ans) -> tuple[str, str]:
    user = getattr(ans, "user_ans", None) or ans.get("user_ans", "")
    correct = getattr(ans, "correct_ans", None) or ans.get("correct_ans", "")
    return user, correct


def _mock_reading_item(
    qid: str,
    user_ans: str,
    correct_ans: str,
    is_correct: bool,
    display_num: str,
    mode: str = "reading",
) -> dict:
    return {
        "question_id": str(qid),
        "display_num": display_num,
        "label": display_num,
        "is_correct": is_correct,
        "correct_answer": correct_ans,
        "error_analysis": (
            "定位准确，同义替换识别到位。"
            if is_correct
            else f"【严厉诊断】第 {display_num} 题错选「{user_ans}」，正确答案「{correct_ans}」。"
            "原文极可能通过否定/转折/偷换概念设置陷阱。"
        ),
        "knowledge_point": "转折词后信息才是答案 · 词义偷换类干扰",
        "reading_tip": (
            "保持定位节奏，继续积累同义替换。"
            if is_correct
            else "回读错题段落，标出定位词、转折词与干扰项出处。"
        ),
        "paraphrase_pairs": [
            {"original": "emphasis", "replacement": "stress / focus"},
            {"original": "widespread", "replacement": "pervasive"},
        ],
    }


def _build_mock_diagnosis(
    exam_id: str,
    all_answers: dict,
    question_meta: list | None,
    passage_excerpt: str,
) -> dict:
    items = normalize_diagnosis_result(
        {"items": {}},
        all_answers,
        question_meta,
        mode="reading",
    )
    if not items:
        items = ensure_diagnosis_items(
            [],
            all_answers,
            question_meta,
            mode="reading",
            mock_item_fn=_mock_reading_item,
        )
    return {
        "exam_id": exam_id,
        "passage_preview": (passage_excerpt or "")[:200],
        "items": items,
    }


async def diagnose_reading(
    exam_id: str,
    wrong_answers: dict,
    passage_excerpt: str = "",
    all_answers: dict | None = None,
    question_meta: list | None = None,
) -> dict:
    merged = dict(all_answers or {})
    if not merged:
        merged = dict(wrong_answers or {})

    answer_payload = {}
    for qid, ans in merged.items():
        user, correct = _normalize_answer(ans)
        answer_payload[qid] = {
            "user_ans": user,
            "correct_ans": correct,
            "objective_status": "正确" if objective_is_correct(user, correct) else "错误",
        }

    q_range = ", ".join(
        str(m.get("num", m.get("id"))) for m in (question_meta or [])
    ) or "见作答列表"

    messages = [
        {"role": "system", "content": reading_diagnosis_system(q_range)},
        {
            "role": "user",
            "content": user_payload(
                exam_id=exam_id,
                question_meta=question_meta or [],
                passage_excerpt=(passage_excerpt or "")[:3000],
                answers=answer_payload,
            ),
        },
    ]

    def mock_fn():
        return _build_mock_diagnosis(exam_id, merged, question_meta, passage_excerpt)

    result = await llm_json_or_mock(messages, mock_fn)
    result.setdefault("exam_id", exam_id)
    result.setdefault("passage_preview", (passage_excerpt or "")[:200])

    if merged:
        result["items"] = normalize_diagnosis_result(result, merged, question_meta, mode="reading")
        result["items"] = ensure_diagnosis_items(
            result["items"],
            merged,
            question_meta,
            mode="reading",
            mock_item_fn=_mock_reading_item,
        )
    else:
        result["items"] = mock_fn()["items"]
    return result


def _mock_assistant_reply(mode: str, text: str, exam_title: str = "") -> str:
    if mode == "word":
        word = text.strip()
        return (
            f"【查词】{word}\n\n"
            f"释义：结合语境理解核心概念。\n\n"
            f"【同义替换追踪】在《{exam_title or '真题'}》中，{word} 常与 "
            f"pervasive / widespread / dominant 等形成上位或近义替换。"
        )
    return (
        f"【长难句成分拆解】\n\n"
        f"原句：{text[:120]}...\n\n"
        f"[主语] It\n[谓语] remains to be seen\n[宾语从句] whether + 完整从句\n\n"
        f"点拨：形式主语 it 仅占位，真正信息在 whether 引导的从句中。"
    )


async def assistant_reply(mode: str, text: str, exam_title: str = "") -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "你是雅思阅读随身助理，回答精准严厉，禁止空泛。"
                "mode=word：查词 + 同义替换追踪；mode=sentence：长难句成分拆解。中文，保留【】标题。"
            ),
        },
        {
            "role": "user",
            "content": json.dumps(
                {"mode": mode, "text": text, "exam_title": exam_title},
                ensure_ascii=False,
            ),
        },
    ]

    try:
        from app.deepseek_client import chat_completion

        content = await chat_completion(messages, temperature=0.2)
        return content.strip() or _mock_assistant_reply(mode, text, exam_title)
    except Exception:
        return _mock_assistant_reply(mode, text, exam_title)
