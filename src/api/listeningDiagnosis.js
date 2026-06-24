import { apiFetch } from './client'
import { normalizeDiagnosisItems, buildListeningQuestionMeta } from '@/utils/diagnosisNormalize'
import { estimatedListeningBand, formatIeltsBand } from '@/utils/ieltsScore'

export async function requestListeningDiagnosis({
  lessonId,
  wrongAnswers,
  allAnswers,
  questionMeta,
}) {
  const meta = questionMeta?.length ? questionMeta : buildListeningQuestionMeta(allAnswers)

  const data = await apiFetch('/api/listening/diagnose', {
    method: 'POST',
    body: JSON.stringify({
      lesson_id: lessonId,
      wrong_answers: wrongAnswers || {},
      all_answers: allAnswers || {},
      question_meta: meta,
    }),
  })

  const items = normalizeDiagnosisItems(data.items, meta, allAnswers, 'listening')
  const correct = items.filter((i) => i.is_correct).length
  const score = data.updated_score ?? estimatedListeningBand(correct, items.length)

  return {
    ...data,
    items,
    updated_score: score,
  }
}
