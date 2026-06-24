from __future__ import annotations

import json
from pathlib import Path

from app.diagnosis_items import ensure_diagnosis_items
from app.diagnosis_normalize import normalize_diagnosis_result
from app.grading_rules import objective_is_correct
from app.lesson_text import extract_lesson_text
from app.llm_helper import llm_json_or_mock
from app.prompt_manager import listening_diagnosis_system, user_payload

LESSON_REGISTRY = {
    "103": {
        "folder": "103. P1 International Club",
        "pdf": "103. P1 International Club.pdf",
        "html": "103. P1 International Club.html",
        "title": "P1 International Club",
        "section": "Part 1",
    },
    "104": {
        "folder": "104. P2 Riding for the Disabled (RDA)",
        "pdf": "104. P2 Riding for the Disabled (RDA).pdf",
        "html": "104. P2 Riding for the Disabled (RDA).html",
        "title": "P2 Riding for the Disabled (RDA)",
        "section": "Part 2",
    },
    "105": {
        "folder": "105. P4 Mass Strandings of Whales and Dolphins",
        "pdf": "105. P4 Mass Strandings of Whales and Dolphins.pdf",
        "html": "105. P4 Mass Strandings of Whales and Dolphins.html",
        "title": "P4 Mass Strandings of Whales and Dolphins",
        "section": "Part 4",
    },
    "p3-103": {
        "folder": "3. P3 Shampoo Marketing Project",
        "pdf": "3. P3 Shampoo Marketing Project.pdf",
        "html": "3. P3 Shampoo Marketing Project.html",
        "title": "P3 Shampoo Marketing Project",
        "section": "Part 3",
    },
}


def _find_listening_root() -> Path | None:
    dashboard = Path(__file__).resolve().parents[2]
    bundled = dashboard / "assets" / "listening"
    if bundled.is_dir():
        return bundled
    parent = Path(__file__).resolve().parents[3]
    for child in parent.iterdir():
        if child.is_dir() and "105" in child.name:
            return child
    return None


def load_lesson_context(lesson_id: str) -> str:
    meta = LESSON_REGISTRY.get(lesson_id)
    if not meta:
        return ""
    root = _find_listening_root()
    if not root:
        return f"[Lesson {lesson_id}] 本地题库目录未找到。"
    folder = root / meta["folder"]
    html_path = folder / meta.get("html", "")
    pdf_path = folder / meta.get("pdf", "")
    text = extract_lesson_text(html_path, pdf_path)
    if text:
        return f"[Lesson {lesson_id} · {meta['title']}]\n{text}"
    if html_path.exists() or pdf_path.exists():
        return f"[Lesson {lesson_id}] 已定位资源但未能提取正文。"
    return f"[Lesson {lesson_id}] 原文文件未找到。"


def _normalize_answer(ans) -> tuple[str, str]:
    user = getattr(ans, "user_ans", None) or ans.get("user_ans", "")
    correct = getattr(ans, "correct_ans", None) or ans.get("correct_ans", "")
    return user, correct


def _mock_item(
    qid: str,
    user_ans: str,
    correct_ans: str,
    is_correct: bool,
    display_num: str,
    mode: str = "listening",
) -> dict:
    return {
        "question_id": qid,
        "display_num": display_num,
        "label": display_num,
        "is_correct": is_correct,
        "correct_answer": correct_ans,
        "error_analysis": (
            "答案正确。注意同义替换与拼写稳定性，勿因语速错过转折后的最终信息。"
            if is_correct
            else f"【严厉诊断】你在第 {display_num} 题填「{user_ans}」，落入干扰项；"
            f"正确答案为「{correct_ans}」。极可能是未跟读 but/however 后的信息修正。"
        ),
        "listening_tip": (
            "保持 1.0x 精听，跟读答案句并标注同义替换。"
            if is_correct
            else "1.0x 精听本题答案句前后 2 句，用 1.25x 跟读，重点听转折词。"
        ),
        "knowledge_point": "时间/数字「先诱后改」+ 同义替换定位",
    }


def _build_mock_diagnosis(
    lesson_id: str,
    wrong_answers: dict,
    all_answers: dict | None,
    context: str,
    question_meta: list | None = None,
) -> dict:
    merged = dict(all_answers or {})
    if not merged:
        merged = dict(wrong_answers or {})

    items = normalize_diagnosis_result(
        {"items": {}},
        merged,
        question_meta,
        mode="listening",
    )
    if not items and merged:
        items = ensure_diagnosis_items(
            [],
            merged,
            question_meta,
            mode="listening",
            mock_item_fn=_mock_item,
        )
    if not items:
        items = [_mock_item("q1", "10:00", "10:30", False, "1")]

    return {
        "lesson_id": lesson_id,
        "context_preview": context[:300],
        "items": items,
    }


async def diagnose_listening(
    lesson_id: str,
    wrong_answers: dict,
    all_answers: dict | None = None,
    question_meta: list | None = None,
) -> dict:
    context = load_lesson_context(lesson_id)
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
        {"role": "system", "content": listening_diagnosis_system(q_range)},
        {
            "role": "user",
            "content": user_payload(
                lesson_id=lesson_id,
                question_meta=question_meta or [],
                context_excerpt=context[:4000],
                answers=answer_payload,
            ),
        },
    ]

    def mock_fn():
        return _build_mock_diagnosis(lesson_id, wrong_answers, all_answers, context, question_meta)

    result = await llm_json_or_mock(messages, mock_fn)
    result.setdefault("lesson_id", lesson_id)
    result.setdefault("context_preview", context[:300])

    if merged:
        result["items"] = normalize_diagnosis_result(result, merged, question_meta, mode="listening")
        result["items"] = ensure_diagnosis_items(
            result["items"],
            merged,
            question_meta,
            mode="listening",
            mock_item_fn=_mock_item,
        )
    else:
        result["items"] = mock_fn()["items"]
    return result


def list_lessons():
    return [{"lesson_id": k, **v} for k, v in LESSON_REGISTRY.items()]
