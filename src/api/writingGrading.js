import { apiFetch } from './client'

export async function requestWritingGrade({ taskId, taskType, essayText, prompt }) {
  try {
    return await apiFetch('/api/writing/grade', {
      method: 'POST',
      body: JSON.stringify({
        task_id: taskId,
        task_type: taskType,
        essay_text: essayText,
        prompt,
      }),
    })
  } catch {
    return mockWritingGrade(essayText, taskType)
  }
}

function mockWritingGrade(essayText, taskType) {
  const words = essayText.trim().split(/\s+/).filter(Boolean).length
  const base = words >= 250 ? 6.5 : words >= 150 ? 6.0 : 5.5
  return {
    source: 'mock',
    overall_score: base,
    sub_scores: {
      TR_TA: Math.min(9, base + 0.5),
      CC: base,
      LR: Math.min(9, base + 0.5),
      GRA: Math.max(4, base - 0.5),
    },
    grammar_highlights: [
      {
        original: 'Technology help us learn',
        corrected: 'Technology helps us learn',
        reason: '主谓一致错误',
      },
    ],
    strengths: ['论点方向清晰', '段落结构基本完整'],
    weaknesses: ['论证深度不足', '衔接词多样性有限'],
    polished_essay:
      taskType === 'task1'
        ? 'The line graph illustrates participant numbers at a Melbourne social centre between 2000 and 2020...'
        : 'There is considerable debate about whether competition benefits society...',
    general_advice: '论证结构清晰，但语法多样性仍有提升空间，建议多使用定语从句与对比连接词。',
  }
}
