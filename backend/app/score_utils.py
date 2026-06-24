from __future__ import annotations


def round_ielts_band(score: float) -> float:
    clamped = max(0.0, min(9.0, float(score)))
    return round(clamped * 2) / 2


def format_ielts_band(score: float) -> str:
    band = round_ielts_band(score)
    return f"{band:.1f}" if band % 1 else f"{int(band)}"


def estimated_listening_band(correct: int, total: int) -> float:
    if total <= 0:
        return 6.0
    ratio = correct / total
    raw = 3.0 + ratio * 6.0
    return round_ielts_band(raw)
