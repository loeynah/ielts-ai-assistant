export function cleanPassageHtml(html) {
  const doc = new DOMParser().parseFromString(html, 'text/html')
  doc
    .querySelectorAll(
      '.paragraph-dropzone, .dropzone, .paragraph-label, #divider, .empty-space',
    )
    .forEach((el) => el.remove())

  doc.querySelectorAll('.paragraph-wrapper').forEach((wrapper) => {
    wrapper.querySelectorAll('p').forEach((p) => {
      wrapper.parentNode?.insertBefore(p.cloneNode(true), wrapper)
    })
    wrapper.remove()
  })

  return doc.body.innerHTML
}

function poolOptions(doc, selector) {
  return [...doc.querySelectorAll(selector)].map((el) => ({
    value: el.dataset.option || el.dataset.heading || el.textContent.trim(),
    label: el.textContent.trim(),
  }))
}

function collectWordPoolOptions(doc) {
  const seen = new Set()
  const items = []
  const nodes = doc.querySelectorAll(
    '.options-pool .drag-item, .pool-items .drag-item, .draggable-word, #word-options .drag-item',
  )
  nodes.forEach((el) => {
    const value =
      el.dataset.option ||
      el.dataset.key ||
      (el.textContent.trim().match(/^([A-Z])\b/)?.[1] ?? '')
    const label = el.textContent.trim()
    if (!value || !label || seen.has(value)) return
    seen.add(value)
    items.push({ value, label })
  })
  return items
}

function buildSummaryHtml(doc, questionDisplayMap) {
  const summaryEl = doc.querySelector('.summary-text, .summary-completion, .summary-box')
  if (!summaryEl) return ''

  const clone = summaryEl.cloneNode(true)
  clone.querySelectorAll('.drop-target-summary[data-question]').forEach((el) => {
    const qKey = el.getAttribute('data-question')
    const num = questionDisplayMap[qKey] || qKey?.replace('q', '') || '?'
    const mark = doc.createElement('strong')
    mark.className = 'summary-blank-mark'
    mark.textContent = `[${num}]`
    el.replaceWith(mark)
  })
  clone.querySelectorAll('input.blank, input.summary-input, input[name^="q"]').forEach((inp) => {
    const name = inp.getAttribute('name')
    const num = questionDisplayMap[name] || name?.replace('q', '') || '?'
    const mark = doc.createElement('strong')
    mark.className = 'summary-blank-mark'
    mark.textContent = `[${num}]`
    inp.replaceWith(mark)
  })
  return clone.innerHTML
}

function summaryQuestionLabel(target, questionDisplayMap) {
  const qKey = target.getAttribute('data-question')
  const num = questionDisplayMap[qKey] || qKey?.replace('q', '') || ''
  const para = target.closest('p, li')
  if (!para) return `选择第 ${num} 空`
  let text = para.textContent.replace(/\s+/g, ' ').trim()
  if (text.length > 140) text = `${text.slice(0, 137)}…`
  return text || `选择第 ${num} 空`
}

function parseRadioOptions(item) {
  return [...item.querySelectorAll('input[type="radio"]')].map((inp) => {
    const labelEl = inp.closest('label')
    return {
      value: inp.value,
      label: labelEl?.textContent?.trim() || inp.value,
    }
  })
}

function detectRadioQuestionType(options) {
  const values = options.map((o) => o.value)
  if (values.every((v) => ['TRUE', 'FALSE', 'NOT GIVEN'].includes(v))) {
    return { type: 'tfng', options: ['TRUE', 'FALSE', 'NOT GIVEN'] }
  }
  if (values.every((v) => ['YES', 'NO', 'NOT GIVEN'].includes(v))) {
    return { type: 'tfng', options: ['YES', 'NO', 'NOT GIVEN'] }
  }
  return { type: 'select', options }
}

function buildIntroHtml(doc) {
  return [...doc.querySelectorAll('.group > p')]
    .slice(0, 6)
    .map((p) => p.outerHTML)
    .join('')
}

function parseMatchingTableQuestions(doc, g, questionDisplayMap, questions) {
  const rows = doc.querySelectorAll('.matching-table tbody tr')
  if (!rows.length) return

  const headerCells = doc.querySelectorAll('.matching-table thead th')
  const letterOptions = [...headerCells]
    .slice(1)
    .map((th) => {
      const value = th.textContent.trim()
      return { value, label: value }
    })
    .filter((o) => o.value)

  rows.forEach((row, idx) => {
    const td = row.querySelector('td')
    const raw = td?.textContent?.trim() || ''
    const numMatch = raw.match(/^(\d+)\s*/)
    const radioName = row.querySelector('input[type="radio"]')?.name
    const qKey = radioName || g.questionIds?.[idx]
    if (!qKey || questions.some((q) => q.id === qKey)) return

    questions.push({
      id: qKey,
      num: questionDisplayMap[qKey] || numMatch?.[1] || String(idx + 1),
      type: 'select',
      label: raw.replace(/^\d+\s*/, ''),
      options: letterOptions,
    })
  })
}

function parseChoiceItemQuestions(doc, g, questionDisplayMap, questions) {
  const items = doc.querySelectorAll('.choice-item')
  if (!items.length) return

  const options = [...items]
    .map((item) => {
      const inp = item.querySelector('input[type="checkbox"], input[type="radio"]')
      return {
        value: inp?.value || '',
        label: item.textContent.trim(),
      }
    })
    .filter((o) => o.value)

  const ids = g.questionIds || []
  for (const qKey of ids) {
    if (questions.some((q) => q.id === qKey)) continue
    const num = questionDisplayMap[qKey] || qKey.replace('q', '')
    questions.push({
      id: qKey,
      num,
      type: 'select',
      label: `选择第 ${num} 题答案`,
      options,
    })
  }
}

function parseMatchDropzoneQuestions(doc, g, questionDisplayMap, countryOptions, headingOptions, questions) {
  doc.querySelectorAll('.match-question-item').forEach((item, idx) => {
    const p = item.querySelector('p')
    const raw = p?.textContent?.trim() || ''
    const numMatch = raw.match(/^(\d+)/)
    const dropzone = item.querySelector('[data-question]')
    const qKey = dropzone?.getAttribute('data-question') || g.questionIds?.[idx]
    if (!qKey || questions.some((q) => q.id === qKey)) return

    const options = countryOptions.length ? countryOptions : headingOptions
    questions.push({
      id: qKey,
      num: questionDisplayMap[qKey] || numMatch?.[1],
      type: 'select',
      label: raw.replace(/^\d+\s*/, ''),
      options,
    })
  })
}

function parseDropTargetQuestions(doc, g, questionDisplayMap, wordPoolOptions, questions) {
  const targets = doc.querySelectorAll('.drop-target-summary[data-question]')
  if (!targets.length) return

  const orderedIds = g.questionIds?.length
    ? g.questionIds.filter((id) =>
        doc.querySelector(`.drop-target-summary[data-question="${id}"]`),
      )
    : [...targets].map((t) => t.getAttribute('data-question'))

  for (const qKey of orderedIds) {
    if (!qKey || questions.some((q) => q.id === qKey)) continue
    const target = doc.querySelector(`.drop-target-summary[data-question="${qKey}"]`)
    questions.push({
      id: qKey,
      num: questionDisplayMap[qKey] || qKey.replace('q', ''),
      type: 'select',
      label: target
        ? summaryQuestionLabel(target, questionDisplayMap)
        : `选择第 ${questionDisplayMap[qKey] || qKey} 空`,
      options: wordPoolOptions,
    })
  }
}

export function parseQuestionGroups(exam) {
  const { questionGroups = [], questionDisplayMap = {} } = exam
  const groups = []

  for (const g of questionGroups) {
    const doc = new DOMParser().parseFromString(g.bodyHtml, 'text/html')
    const title = doc.querySelector('h4')?.textContent?.trim() || 'Questions'
    const introHtml = buildIntroHtml(doc)

    const questions = []
    const headingOptions = poolOptions(doc, '.headings-pool .drag-item')
    const countryOptions = poolOptions(doc, '.options-pool .drag-item')
    const wordPoolOptions = collectWordPoolOptions(doc)
    const summaryHtml = buildSummaryHtml(doc, questionDisplayMap)

    parseDropTargetQuestions(doc, g, questionDisplayMap, wordPoolOptions, questions)
    parseMatchingTableQuestions(doc, g, questionDisplayMap, questions)
    parseChoiceItemQuestions(doc, g, questionDisplayMap, questions)

    doc.querySelectorAll('.question-item').forEach((item, idx) => {
      const radioOpts = parseRadioOptions(item)
      if (radioOpts.length < 2) return

      const p = item.querySelector('p')
      const raw = p?.textContent?.trim() || ''
      const numMatch = raw.match(/^(\d+)\.?\s*/)
      const radioName = item.querySelector('input[type="radio"]')?.name
      const qKey =
        radioName ||
        g.questionIds?.[idx] ||
        (numMatch ? `q${numMatch[1]}` : `q${idx + 1}`)

      if (questions.some((q) => q.id === qKey)) return

      const { type, options } = detectRadioQuestionType(radioOpts)
      questions.push({
        id: qKey,
        num: questionDisplayMap[qKey] || numMatch?.[1] || String(idx + 1),
        type,
        label: raw.replace(/^\d+\.?\s*/, ''),
        options,
      })
    })

    parseMatchDropzoneQuestions(
      doc,
      g,
      questionDisplayMap,
      countryOptions,
      headingOptions,
      questions,
    )

    doc
      .querySelectorAll('input.blank, input.summary-input, input[name^="q"][type="text"]')
      .forEach((inp) => {
        const name = inp.getAttribute('name')
        if (!name || questions.some((q) => q.id === name)) return
        const ctx = inp.closest('p, .bullet-point, .notes-section, li')
        questions.push({
          id: name,
          num: questionDisplayMap[name] || name.replace('q', ''),
          type: 'blank',
          label: ctx?.textContent?.replace(/\s+/g, ' ').trim() || `Question ${name}`,
          placeholder: 'ONE WORD AND/OR A NUMBER',
        })
      })

    if (g.kind === 'matching' && headingOptions.length && questions.length === 0) {
      g.questionIds?.forEach((qKey, i) => {
        questions.push({
          id: qKey,
          num: questionDisplayMap[qKey] || String(i + 1),
          type: 'select',
          label: `Paragraph ${String.fromCharCode(65 + i)} — 选择最佳标题`,
          options: headingOptions,
        })
      })
    }

    if (g.questionIds?.length) {
      questions.sort(
        (a, b) => g.questionIds.indexOf(a.id) - g.questionIds.indexOf(b.id),
      )
    }

    groups.push({
      groupId: g.groupId,
      title,
      introHtml,
      summaryHtml,
      wordPoolOptions,
      questions,
    })
  }

  return groups
}
