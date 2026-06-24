from __future__ import annotations

from app.chat_parser import parse_chat_response
from app.deepseek_client import chat_completion
from app.prompt_manager import chat_butler_system
from app.time_context import days_until

PLAN_KEYWORDS = ("计划", "plan", "安排", "训练", "备考", "打卡", "日程", "冲刺", "复习", "倒计时", "报名", "考试")


async def build_plan_reply(user_message: str, user_profile: dict | None = None) -> dict:
    profile = user_profile or {}
    exam_date = profile.get("exam_date") or None
    target_score = profile.get("target_score")
    if target_score is not None and target_score < 0:
        target_score = None
    countdown = days_until(exam_date)

    system = chat_butler_system(exam_date, target_score, countdown)

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_message},
    ]

    try:
        raw = (await chat_completion(messages, temperature=0.5)).strip()
        parsed = parse_chat_response(raw)
        wants_plan = any(k in user_message for k in PLAN_KEYWORDS) or bool(parsed["today_tasks"])

        result = {
            "content": parsed["content"],
            "actions": [],
            "emit_plan": False,
            "today_tasks": parsed["today_tasks"],
            "exam_date": parsed.get("exam_date"),
            "target_score": parsed.get("target_score"),
        }

        if wants_plan and (parsed["today_tasks"] or any(k in user_message for k in PLAN_KEYWORDS)):
            result["actions"] = [
                {"id": "sync-plan", "label": "将此计划一键同步至今日打卡清单"},
                {"id": "keep-plan", "label": "保持原计划不变"},
            ]
            result["emit_plan"] = True

        return result
    except Exception as exc:
        return {
            "content": (
                f"抱歉，AI 调用失败：{exc}\n\n"
                "请检查 backend/.env：DEEPSEEK_API_KEY 是否已填入 SiliconFlow Key，"
                "DEEPSEEK_BASE_URL=https://api.siliconflow.cn/v1，"
                "DEEPSEEK_MODEL=deepseek-ai/DeepSeek-V3；修改后重启后端。"
            ),
            "actions": [],
            "emit_plan": False,
            "today_tasks": [],
        }
