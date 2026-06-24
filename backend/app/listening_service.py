"""听力切片诊断 — PDF/HTML 上下文 + DeepSeek-V3 结构化 JSON"""
from __future__ import annotations

import json
from pathlib import Path

from app.diagnosis_items import ensure_diagnosis_items
from app.lesson_text import extract_lesson_text
from app.llm_helper import llm_json_or_mock

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
            "答案正确，注意同义替换与拼写稳定性。"
            if is_correct
            else f"你在「{user_ans}」处落入了前半句干扰，正确答案为「{correct_ans}」。"
        ),
        "listening_tip": (
            "保持当前精听节奏，重点跟读答案句。"
            if is_correct
            else "建议 1.0x 精听转折词 but / actually 前后 2 句，并用 1.25x 跟读答案句。"
        ),
        "knowledge_point": "时间信息「先诱后改」+ 同义替换定位",
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

    items = ensure_diagnosis_items(
        [],
        merged,
        question_meta,
        mode="listening",
        mock_item_fn=_mock_item,
    ) if merged else [_mock_item("q1", "10:00", "10:30", False, "1")]

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

    answer_payload = {
        qid: {"user_ans": _normalize_answer(ans)[0], "correct_ans": _normalize_answer(ans)[1]}
        for qid, ans in merged.items()
    }
    if not answer_payload:
        answer_payload = {"q1": {"user_ans": "10:00", "correct_ans": "10:30"}}

    messages = [
        {
            "role": "system",
            "content": (
                "你是雅思听力教研专家。根据原文与学生全部作答，为每一道题输出诊断 JSON："
                '{"items":[{"question_id","label","is_correct","correct_answer",'
                '"display_num":"1","label":"1","is_correct","correct_answer",'
                '"error_analysis","listening_tip","knowledge_point"}]}'
                "。必须为每道题都生成一条 items；label/display_num 必须为真实题号数字，禁止用题型名。用中文写分析。"
            ),
        },
        {
            "role": "user",
            "content": (
                f"Lesson: {lesson_id}\n\n原文节选：\n{context[:4000]}\n\n"
                f"学生全部作答（共 {len(answer_payload)} 题）：\n"
                f"{json.dumps(answer_payload, ensure_ascii=False)}"
            ),
        },
    ]

    def mock_fn():
        return _build_mock_diagnosis(lesson_id, wrong_answers, all_answers, context, question_meta)

    result = await llm_json_or_mock(messages, mock_fn)
    result.setdefault("lesson_id", lesson_id)
    result.setdefault("context_preview", context[:300])
    if "items" not in result:
        return mock_fn()
    result["items"] = ensure_diagnosis_items(
        result["items"],
        merged,
        question_meta,
        mode="listening",
        mock_item_fn=_mock_item,
    )
    return result


def list_lessons():
    return [{"lesson_id": k, **v} for k, v in LESSON_REGISTRY.items()]
