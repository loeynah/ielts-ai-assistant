"""写作四维度阅卷 — DeepSeek-V3 结构化输出"""
from __future__ import annotations

import json

from app.llm_helper import llm_json_or_mock


def _build_mock_grade(task_id: str, task_type: str, essay_text: str) -> dict:
    words = len([w for w in essay_text.strip().split() if w])
    min_words = 150 if task_type == "task1" else 250
    base = 6.5 if words >= min_words else 6.0 if words >= min_words * 0.7 else 5.5

    return {
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
                "reason": "主谓一致错误",
            },
        ],
        "strengths": ["论点方向清晰", "段落结构基本完整"],
        "weaknesses": ["论证深度不足", "衔接词多样性有限", "语法句式偏单一"],
        "polished_essay": _sample_polished(task_type),
        "general_advice": (
            "论证结构清晰，但语法多样性（GRA）仍有提升空间，"
            "建议多使用定语从句、分词结构和对比连接词增强逻辑衔接。"
        ),
    }


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


async def grade_writing(task_id: str, task_type: str, essay_text: str, prompt: str) -> dict:
    messages = [
        {
            "role": "system",
            "content": (
                "你是雅思写作考官。按 TR/TA、CC、LR、GRA 四维度评分，输出 JSON："
                '{"overall_score":6.5,"sub_scores":{"TR_TA","CC","LR","GRA"},'
                '"grammar_highlights":[{"original","corrected","reason"}],'
                '"strengths":[],"weaknesses":[],"polished_essay":"","general_advice":""}'
                "。分数 0-9，保留一位小数。分析与建议用中文。"
            ),
        },
        {
            "role": "user",
            "content": json.dumps(
                {
                    "task_id": task_id,
                    "task_type": task_type,
                    "prompt": prompt,
                    "essay_text": essay_text[:6000],
                },
                ensure_ascii=False,
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
    return result
