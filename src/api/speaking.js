import { apiFetch } from './client'

export async function requestSpeakingExamGrade({ examId, part1, part2, part3 }) {
  return await apiFetch('/api/speaking/grade-exam', {
    method: 'POST',
    body: JSON.stringify({
      exam_id: examId,
      part1: part1 || [],
      part2: part2 || null,
      part3: part3 || [],
    }),
  })
}

export async function requestSpeakingPracticeGrade({ question, transcript, duration = 0 }) {
  return await apiFetch('/api/speaking/grade-practice', {
    method: 'POST',
    body: JSON.stringify({ question, transcript, duration }),
  })
}
