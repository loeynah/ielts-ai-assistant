const INVALID_MARKERS = ['未检测到有效语音', '无转写文本', '未作答']

export function isValidTranscriptText(text, minChars = 8) {
  const t = String(text || '').trim()
  if (!t || t === '—' || t === '-') return false
  if (INVALID_MARKERS.some((m) => t.includes(m))) return false
  return t.length >= minChars
}

export function hasValidSpeakingAnswer(
  { transcript, duration },
  { minChars = 8, minSeconds = 2 } = {},
) {
  const dur = Number(duration) || 0
  if (dur > 0 && dur < minSeconds) return false
  return isValidTranscriptText(transcript, minChars)
}

export function countValidExamAnswers(payload) {
  let count = 0
  for (const item of payload.part1 || []) {
    if (hasValidSpeakingAnswer(item)) count += 1
  }
  if (payload.part2 && hasValidSpeakingAnswer(payload.part2)) count += 1
  for (const item of payload.part3 || []) {
    if (hasValidSpeakingAnswer(item)) count += 1
  }
  return count
}
