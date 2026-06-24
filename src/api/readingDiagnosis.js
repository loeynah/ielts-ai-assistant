import { apiFetch } from './client'
import { normalizeDiagnosisItems } from '@/utils/diagnosisNormalize'
import { estimatedListeningBand } from '@/utils/ieltsScore'

export async function requestReadingDiagnosis({
  examId,
  wrongAnswers,
  allAnswers,
  questionMeta,
  passageText,
}) {
  const data = await apiFetch('/api/reading/diagnose', {
    method: 'POST',
    body: JSON.stringify({
      exam_id: examId,
      wrong_answers: wrongAnswers || {},
      all_answers: allAnswers || {},
      question_meta: questionMeta || [],
      passage_excerpt: passageText?.slice(0, 2000),
    }),
  })

  const items = normalizeDiagnosisItems(
    data.items,
    questionMeta,
    allAnswers,
    'reading',
  )
  const correct = items.filter((i) => i.is_correct).length
  const score = data.updated_score ?? estimatedListeningBand(correct, items.length)

  return {
    ...data,
    items,
    updated_score: score,
  }
}

export async function requestReadingAssistant({ mode, text, examTitle }) {
  try {
    const res = await apiFetch('/api/reading/assistant', {
      method: 'POST',
      body: JSON.stringify({ mode, text, exam_title: examTitle }),
    })
    return res.reply
  } catch {
    return mockAssistantReply(mode, text, examTitle)
  }
}

export function mockAssistantReply(mode, text, examTitle) {
  if (mode === 'word') {
    const word = text.trim()
    return `【查词】${word}\n\n释义：根据语境可理解为关键概念词。\n\n【同义替换追踪】在《${examTitle || '真题'}》中，${word} 常与 pervasive / widespread 等形成近义替换。`
  }
  return `【长难句拆解】\n\n"${text.slice(0, 100)}..."\n\n[主语] It\n[谓语] remains to be seen\n[宾语从句] whether + 从句\n\n点拨：真正信息在 whether 引导的从句中。`
}
