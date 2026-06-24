"""阅读切片诊断 + 随身助理"""
from __future__ import annotations

import json

from app.diagnosis_items import ensure_diagnosis_items
from app.llm_helper import llm_json_or_mock


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
            else f"错因定位：你将「{user_ans}」误判为正确，原文通过否定/转折指向「{correct_ans}」。"
        ),
        "knowledge_point": "转折词后信息才是答案 · 词义偷换类干扰",
        "reading_tip": (
            "保持当前定位节奏，继续积累同义替换。"
            if is_correct
            else "建议回读错题所在段落，标出转折词与定位词。"
        ),
        "paraphrase_pairs": [
            {"original": "emphasis", "replacement": "stress / focus"},
            {"original": "widespread", "replacement": "pervasive / ubiquitous"},
        ],
    }


def _build_mock_diagnosis(
    exam_id: str,
    all_answers: dict,
    question_meta: list | None,
    passage_excerpt: str,
) -> dict:
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

    answer_payload = {
        qid: {"user_ans": _normalize_answer(ans)[0], "correct_ans": _normalize_answer(ans)[1]}
        for qid, ans in merged.items()
    }

    meta_hint = json.dumps(question_meta or [], ensure_ascii=False)
    q_range = ", ".join(
        str(m.get("num", m.get("id"))) for m in (question_meta or [])
    ) or "见作答列表"

    messages = [
        {
            "role": "system",
            "content": (
                "你是雅思阅读教研专家。必须为每一道题输出诊断，JSON 格式："
                '{"items":[{"question_id":"q1","display_num":"1","label":"1",'
                '"is_correct":true,"correct_answer":"","error_analysis":"",'
                '"knowledge_point":"","reading_tip":"",'
                '"paraphrase_pairs":[{"original":"","replacement":""}]}]}'
                f"。question_id 必须与输入一致；label/display_num 必须为真实题号（{q_range}），"
                "禁止用题型名称代替题号。用中文写分析。"
            ),
        },
        {
            "role": "user",
            "content": (
                f"Exam: {exam_id}\n题号元数据：{meta_hint}\n\n"
                f"文章节选：\n{(passage_excerpt or '')[:3000]}\n\n"
                f"学生全部作答（共 {len(answer_payload)} 题）：\n"
                f"{json.dumps(answer_payload, ensure_ascii=False)}"
            ),
        },
    ]

    def mock_fn():
        return _build_mock_diagnosis(exam_id, merged, question_meta, passage_excerpt)

    result = await llm_json_or_mock(messages, mock_fn)
    result.setdefault("exam_id", exam_id)
    result.setdefault("passage_preview", (passage_excerpt or "")[:200])
    if "items" not in result:
        return mock_fn()
    result["items"] = ensure_diagnosis_items(
        result["items"],
        merged,
        question_meta,
        mode="reading",
        mock_item_fn=_mock_reading_item,
    )
    return result


def _mock_assistant_reply(mode: str, text: str, exam_title: str = "") -> str:
    if mode == "word":
        word = text.strip()
        return (
            f"【查词】{word}\n\n"
            f"释义：根据语境可理解为关键概念词。\n\n"
            f"【雅思阅读同义替换追踪】在《{exam_title or '真题'}》中，{word} 常与 "
            f"pervasive / widespread / dominant 等形成上位或近义替换，做题时请主动搜寻。"
        )
    return (
        f"【长难句成分拆解】\n\n"
        f"原句：{text[:120]}...\n\n"
        f"[主语] It\n"
        f"[谓语] remains to be seen\n"
        f"[宾语从句] whether + 完整从句\n\n"
        f"点拨：形式主语 it 仅占位，真正信息在 whether 引导的从句中。"
    )


async def assistant_reply(mode: str, text: str, exam_title: str = "") -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "你是雅思阅读随身助理。mode=word 时输出查词+同义替换追踪；"
                "mode=sentence 时输出长难句成分拆解。使用中文，保留【】标题格式。"
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

        content = await chat_completion(messages, temperature=0.3)
        return content.strip() or _mock_assistant_reply(mode, text, exam_title)
    except Exception:
        return _mock_assistant_reply(mode, text, exam_title)
