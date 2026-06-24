from __future__ import annotations

from app.grading_rules import apply_writing_penalties, count_words
from app.llm_helper import llm_json_or_mock
from app.prompt_manager import user_payload, writing_grade_system


def _build_mock_grade(task_id: str, task_type: str, essay_text: str) -> dict:
    words = count_words(essay_text)
    min_words = 150 if task_type == "task1" else 250
    base = 6.5 if words >= min_words else 5.5 if words >= min_words * 0.7 else 4.5

    result = {
        "task_id": task_id,
        "task_type": task_type,
        "overall_score": base,
        "sub_scores": {
            "TR_TA": round(min(9.0, base + 0.5), 1),
            "CC": base,
            "LR": round(min(9.0, base + 0.5), 1),
            "GRA": round(max(4.0, base - 0.5), 1),
        },
        "grammar_highlights": [
            {
                "original": "Technology help us learn",
                "corrected": "Technology helps us learn",
                "reason": "主谓一致错误 — 典型中式英语硬伤",
            },
        ],
        "strengths": ["论点方向基本清晰"],
        "weaknesses": ["论证深度不足", "衔接词单一", "若字数不足则 TR 必须低分"],
        "polished_essay": _sample_polished(task_type),
        "general_advice": "论证结构尚可，但语法多样性与词汇精准度需加强，严禁回避字数惩罚。",
    }
    return _sanitize_writing(result, task_type, essay_text)


def _sample_polished(task_type: str) -> str:
    if task_type == "task1":
        return (
            "The line graph illustrates participant numbers at a Melbourne social centre "
            "across five activities between 2000 and 2020. Overall, film club remained the "
            "most popular, while table tennis rose sharply in the final decade."
        )
    return (
        "There is considerable debate about whether competition benefits individuals and society. "
        "This essay will discuss both views before presenting my own opinion."
    )


def _sanitize_writing(result: dict, task_type: str, essay_text: str) -> dict:
    sub = result.get("sub_scores") or {}
    overall = float(result.get("overall_score", 6.0))
    sub, overall, extra = apply_writing_penalties(task_type, essay_text, sub, overall)

    weaknesses = list(result.get("weaknesses") or [])
    weaknesses.extend(extra)

    general = result.get("general_advice") or ""
    if extra:
        general = extra[0] + (" " + general if general else "")

    result["sub_scores"] = sub
    result["overall_score"] = overall
    result["weaknesses"] = weaknesses[:8]
    result["general_advice"] = general
    return result


async def grade_writing(task_id: str, task_type: str, essay_text: str, prompt: str) -> dict:
    wc = count_words(essay_text)
    messages = [
        {"role": "system", "content": writing_grade_system()},
        {
            "role": "user",
            "content": user_payload(
                task_id=task_id,
                task_type=task_type,
                word_count=wc,
                prompt=prompt,
                essay_text=essay_text[:6000],
            ),
        },
    ]

    def mock_fn():
        return _build_mock_grade(task_id, task_type, essay_text)

    result = await llm_json_or_mock(messages, mock_fn)
    result.setdefault("task_id", task_id)
    result.setdefault("task_type", task_type)
    if "overall_score" not in result:
        return mock_fn()
    return _sanitize_writing(result, task_type, essay_text)
