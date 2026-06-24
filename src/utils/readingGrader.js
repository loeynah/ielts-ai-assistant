export function normalizeAnswer(val) {
  return String(val ?? '')
    .trim()
    .toLowerCase()
    .replace(/\s+/g, ' ')
}

export function estimateBand(correct, total) {
  if (!total) return 0
  const raw = (correct / total) * 9
  return Math.round(raw * 2) / 2
}

export function gradeReadingAnswers(userAnswers, answerKey) {
  const results = {}
  let correct = 0
  const total = Object.keys(answerKey).length

  for (const [qid, expected] of Object.entries(answerKey)) {
    const user = (userAnswers[qid] || '').trim()
    if (!user) {
      results[qid] = 'unanswered'
      continue
    }
    const isCorrect = normalizeAnswer(user) === normalizeAnswer(expected)
    results[qid] = isCorrect ? 'correct' : 'incorrect'
    if (isCorrect) correct += 1
  }

  const allAnswers = {}
  for (const [qid, expected] of Object.entries(answerKey)) {
    const user = (userAnswers[qid] || '').trim()
    allAnswers[qid] = {
      user_ans: user || '—',
      correct_ans: String(expected ?? ''),
    }
  }

  return {
    results,
    correct,
    total,
    band: estimateBand(correct, total),
    wrongAnswers: buildWrongAnswers(userAnswers, answerKey, results),
    allAnswers,
  }
}

function buildWrongAnswers(userAnswers, answerKey, results) {
  const wrong = {}
  for (const [qid, status] of Object.entries(results)) {
    if (status === 'incorrect') {
      wrong[qid] = {
        user_ans: userAnswers[qid] || '—',
        correct_ans: answerKey[qid],
      }
    }
  }
  return wrong
}
