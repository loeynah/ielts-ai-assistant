"""系统时间上下文 — 注入 LLM System Prompt"""
from __future__ import annotations

from datetime import date, datetime, timezone


def get_current_date() -> date:
    return datetime.now(timezone.utc).date()


def get_current_date_iso() -> str:
    return get_current_date().isoformat()


def days_until(exam_date_iso: str) -> int:
    try:
        target = date.fromisoformat(exam_date_iso)
    except ValueError:
        return 0
    today = get_current_date()
    return max(0, (target - today).days)


def build_time_system_prompt() -> str:
    today = get_current_date()
    iso = today.isoformat()
    return (
        f"【系统锁定信息】：今天是 {today.year} 年 {today.month} 月 {today.day} 日（{iso}）。"
        f"请以此日期作为计算倒计时和生成备考计划的唯一绝对基准，禁止臆造与今天不符的天数或月份跨度。"
    )
