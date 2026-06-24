"""主页 AI 智能管家 — 时间注入 + 结构化任务输出"""
from __future__ import annotations

from app.chat_parser import parse_chat_response
from app.deepseek_client import chat_completion
from app.time_context import build_time_system_prompt, days_until

PLAN_KEYWORDS = ("计划", "plan", "安排", "训练", "备考", "打卡", "日程", "冲刺", "复习")


async def build_plan_reply(user_message: str, user_profile: dict | None = None) -> dict:
    profile = user_profile or {}
    exam_date = profile.get("exam_date", "2026-06-25")
    target_score = profile.get("target_score", 7.0)
    countdown = days_until(exam_date)

    system = (
        build_time_system_prompt()
        + "\n\n你是雅思 AI 智能管家。请根据用户具体问题灵活回答，禁止套用固定模板。"
        f"\n用户当前画像：考试日期 {exam_date}（距今天还有 {countdown} 天），目标分 {target_score}。"
        "\n能力：考试流程科普、英文答疑、基于真实倒计时的备考计划。"
        "\n要求：中文、结构清晰、直接回应用户每个要点；计划天数不得超过距考试剩余天数。"
        "\n\n当回复涉及备考计划或可执行今日任务时，必须在正文之后附加以下结构化块（前端会自动剥离）："
        "\n[META]"
        "\nexam_date: YYYY-MM-DD（用户修改考试日期时更新，否则保持当前值）"
        "\ntarget_score: 数字（用户修改目标分时更新）"
        "\n[/META]"
        "\n[TODAY_TASKS]"
        "\nlistening|今日听力任务（一行一条）"
        "\nspeaking|今日口语任务"
        "\n[/TODAY_TASKS]"
        "\ncategory 仅可为 listening/reading/speaking/writing。"
    )

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_message},
    ]

    try:
        raw = (await chat_completion(messages, temperature=0.7)).strip()
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
                "请检查 backend/.env 中的 DEEPSEEK_API_KEY 是否正确，修改后重启后端。"
            ),
            "actions": [],
            "emit_plan": False,
            "today_tasks": [],
        }
