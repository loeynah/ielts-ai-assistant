/** 雅思分数：仅 0.5 进制 */
export function roundIeltsBand(score) {
  const clamped = Math.max(0, Math.min(9, Number(score) || 0))
  return Math.round(clamped * 2) / 2
}

export function formatIeltsBand(score) {
  const band = roundIeltsBand(score)
  return Number.isInteger(band) ? String(band) : band.toFixed(1)
}

/** 未设定（null / undefined / 负数）时显示 — */
export function formatOptionalBand(score) {
  if (score == null || score < 0) return '—'
  return formatIeltsBand(score)
}

export function estimatedListeningBand(correct, total) {
  if (!total) return 6
  const ratio = correct / total
  return roundIeltsBand(3 + ratio * 6)
}
