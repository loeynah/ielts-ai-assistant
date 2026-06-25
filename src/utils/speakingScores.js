/** 口语四维度分 — 统一 FC/LR/GRA/P 大小写读取 */
export function normalizeSpeakingSubScores(raw, overall = 0) {
  const s = raw || {}
  const base = Number(overall) || 0
  const pick = (key) => {
    const v = s[key] ?? s[key.toLowerCase()] ?? s[key.toUpperCase()]
    const n = Number(v)
    return Number.isFinite(n) ? n : base
  }
  return {
    FC: pick('FC'),
    LR: pick('LR'),
    GRA: pick('GRA'),
    P: pick('P'),
  }
}

export function subScoreFromHistory(record, key) {
  return normalizeSpeakingSubScores(record?.sub_scores, record?.overall_score)[key] ?? 0
}
