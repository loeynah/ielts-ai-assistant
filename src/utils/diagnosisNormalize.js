/** 将题组扁平化为有序题目列表 */
export function flattenReadingQuestions(groups) {
  const list = []
  for (const g of groups || []) {
    for (const q of g.questions || []) {
      const num = String(q.num ?? q.id?.replace(/^q/i, '') ?? '')
      list.push({
        id: q.id,
        num,
        groupTitle: g.title,
      })
    }
  }
  return sortByNum(list)
}

/** 阅读：从答案键构建全部作答 */
export function buildReadingAllAnswers(userAnswers, answerKey) {
  const all = {}
  for (const [qid, expected] of Object.entries(answerKey || {})) {
    const user = (userAnswers[qid] || '').trim()
    all[qid] = {
      user_ans: user || '—',
      correct_ans: String(expected ?? ''),
    }
  }
  return all
}

/** 听力：从 iframe 批改结果构建题目元数据 */
export function buildListeningQuestionMeta(allAnswers) {
  return sortByNum(
    Object.keys(allAnswers || {}).map((qid) => ({
      id: qid,
      num: String(qid).replace(/^q/i, ''),
    })),
  )
}

function sortByNum(list) {
  return [...list].sort((a, b) => {
    const na = parseInt(a.num, 10)
    const nb = parseInt(b.num, 10)
    if (!Number.isNaN(na) && !Number.isNaN(nb)) return na - nb
    return String(a.num).localeCompare(String(b.num), undefined, { numeric: true })
  })
}

function resolveApiItem(apiItems, q) {
  const items = apiItems || []
  return (
    items.find((i) => i.question_id === q.id) ||
    items.find((i) => i.question_id === q.num) ||
    items.find((i) => i.question_id === `q${q.num}`) ||
    items.find((i) => String(i.label).replace(/^Q/i, '') === String(q.num))
  )
}

function defaultAnalysis(isCorrect, user, correct, mode) {
  if (isCorrect) {
    return mode === 'listening'
      ? '答案正确，注意同义替换与拼写稳定性。'
      : '定位准确，同义替换识别到位。'
  }
  return `错因定位：你将「${user || '未作答'}」误判为正确，正确答案为「${correct}」。`
}

/** 将 API 返回与本地全量题目合并，保证题号 Tab 与刷题区一致 */
export function normalizeDiagnosisItems(apiItems, questionMeta, allAnswers, mode = 'reading') {
  const meta = questionMeta?.length
    ? questionMeta
    : sortByNum(
        Object.keys(allAnswers || {}).map((id) => ({
          id,
          num: String(id).replace(/^q/i, ''),
        })),
      )

  return meta.map((q) => {
    const ans = allAnswers[q.id] || allAnswers[`q${q.num}`] || {}
    const user = (ans.user_ans ?? '').trim()
    const correct = (ans.correct_ans ?? '').trim()
    const localCorrect =
      user &&
      user !== '—' &&
      user.toLowerCase() === correct.toLowerCase()
    const api = resolveApiItem(apiItems, q)

    const isCorrect = api?.is_correct ?? localCorrect

    return {
      question_id: q.id,
      display_num: q.num,
      label: String(q.num),
      is_correct: Boolean(isCorrect),
      correct_answer: api?.correct_answer ?? correct,
      error_analysis: api?.error_analysis ?? defaultAnalysis(isCorrect, user, correct, mode),
      knowledge_point:
        api?.knowledge_point ??
        (mode === 'listening'
          ? '时间信息「先诱后改」+ 同义替换定位'
          : '转折词后信息才是答案 · 词义偷换类干扰'),
      listening_tip:
        api?.listening_tip ??
        (isCorrect
          ? '保持当前精听节奏，重点跟读答案句。'
          : '建议 1.0x 精听转折词前后 2 句，并用 1.25x 跟读答案句。'),
      reading_tip:
        api?.reading_tip ??
        (isCorrect
          ? '保持当前定位节奏，继续积累同义替换。'
          : '建议回读错题所在段落，标出转折词与定位词。'),
      paraphrase_pairs: api?.paraphrase_pairs ?? [],
    }
  })
}
