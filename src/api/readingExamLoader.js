const EXAM_BASE = '/assets/reading-exams'

export async function loadReadingExam(examId) {
  const res = await fetch(`${EXAM_BASE}/${examId}.js`)
  if (!res.ok) throw new Error(`无法加载阅读真题: ${examId}`)
  const text = await res.text()
  const match = text.match(/\.register\(\s*["'][^"']+["']\s*,\s*(\{[\s\S]*\})\s*\)\s*;/)
  if (!match) throw new Error(`解析阅读真题失败: ${examId}`)
  // eslint-disable-next-line no-new-func
  return new Function(`return ${match[1]}`)()
}
