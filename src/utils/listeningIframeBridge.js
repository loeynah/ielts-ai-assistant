export const LISTENING_IFRAME_CSS = `
  .header,
  .audio-sticky,
  .bottom-bar,
  .notes-sidebar,
  #selectionToolbar,
  #toastMsg,
  #settingsPanel,
  .overlay,
  #reviewTablesContainer,
  .splitter,
  .right-pane {
    display: none !important;
  }
  body, html {
    overflow: hidden !important;
    height: auto !important;
    background: #ffffff !important;
    margin: 0 !important;
    padding: 0 !important;
  }
  .app-shell {
    height: auto !important;
    min-height: 0 !important;
  }
  .split-layout {
    display: block !important;
    overflow: visible !important;
  }
  .split-view .left-pane {
    flex-basis: 100% !important;
    width: 100% !important;
  }
  .left-pane {
    overflow: visible !important;
    width: 100% !important;
    flex: none !important;
  }
  .test-container {
    padding: 8px 28px 32px !important;
    max-width: 100% !important;
  }
  .blank-input.ielts-dash-correct {
    border-color: #22c55e !important;
    background: #f0fdf4 !important;
    box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.18) !important;
  }
  .blank-input.ielts-dash-incorrect {
    border-color: #ef4444 !important;
    background: #fef2f2 !important;
    box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.15) !important;
  }
`

const DISCLAIMER_RE = /虾滑|@Listening|禁止商用|倒卖和引流/

export function purgeDisclaimerNodes(doc) {
  if (!doc?.body) return

  const removeNode = (node) => {
    if (!node) return
    if (node.nodeType === Node.TEXT_NODE && DISCLAIMER_RE.test(node.textContent)) {
      node.remove()
      return
    }
    if (node.nodeType === Node.ELEMENT_NODE) {
      const text = node.textContent?.trim() || ''
      if (
        text.length < 400 &&
        DISCLAIMER_RE.test(text) &&
        !node.querySelector('.blank-input, .test-container, .question-item')
      ) {
        node.remove()
        return
      }
      ;[...node.childNodes].forEach(removeNode)
    }
  }

  ;[...doc.body.childNodes].forEach(removeNode)
}

export function injectListeningStyles(iframe) {
  try {
    const doc = iframe.contentDocument
    if (!doc) return false

    let style = doc.getElementById('ielts-dashboard-inject')
    if (!style) {
      style = doc.createElement('style')
      style.id = 'ielts-dashboard-inject'
      doc.head.appendChild(style)
    }
    style.textContent = LISTENING_IFRAME_CSS
    purgeDisclaimerNodes(doc)
    return true
  } catch {
    return false
  }
}

export function syncQuestionNav(iframe) {
  try {
    const doc = iframe.contentDocument
    if (!doc) return []
    return [...doc.querySelectorAll('.q-nav-item')].map((el) => ({
      id: el.dataset.q || el.textContent.trim(),
      answered: el.classList.contains('answered'),
      correct: el.classList.contains('correct'),
      incorrect: el.classList.contains('incorrect'),
    }))
  } catch {
    return []
  }
}

export function scrollToQuestion(iframe, qId) {
  try {
    const doc = iframe.contentDocument
    if (!doc) return
    const input =
      doc.getElementById(`input_${qId}`) ||
      doc.querySelector(`[name="q${qId}"]`) ||
      doc.querySelector(`.blank-input[data-q="${qId}"]`)
    if (input) {
      input.scrollIntoView({ behavior: 'smooth', block: 'center' })
      input.focus()
    }
  } catch {
    /* same-origin */
  }
}

function triggerFinishReview(doc) {
  const finishBtn = doc.getElementById('finishBtn')
  if (!finishBtn) return false
  const label = finishBtn.innerText.trim()
  if (label === 'Finish') {
    finishBtn.click()
    return true
  }
  return label.includes('Return')
}

function parseResultRows(doc) {
  const rows = [...doc.querySelectorAll('.results-table tbody tr')]
  const results = []
  rows.forEach((row) => {
    const cells = row.querySelectorAll('td')
    if (cells.length < 4) return
    const num = cells[0].textContent.trim()
    const userAns = cells[1].textContent.trim()
    const correctAns = cells[2].textContent.trim()
    const isCorrect =
      cells[3].classList.contains('correct-tag') ||
      cells[3].textContent.includes('✔') ||
      cells[3].textContent.includes('Correct')
    results.push({ num, userAns, correctAns, isCorrect })
  })
  return results
}

function applyInputHighlights(doc, results) {
  doc.querySelectorAll('.blank-input').forEach((inp) => {
    inp.classList.remove('ielts-dash-correct', 'ielts-dash-incorrect')
  })
  results.forEach(({ num, isCorrect }) => {
    const inp = doc.getElementById(`input_${num}`)
    if (inp) {
      inp.classList.add(isCorrect ? 'ielts-dash-correct' : 'ielts-dash-incorrect')
    }
  })
}

export function submitObjectiveAnswers(iframe) {
  try {
    const doc = iframe.contentDocument
    if (!doc) return null

    injectListeningStyles(iframe)
    triggerFinishReview(doc)

    let results = parseResultRows(doc)
    if (!results.length) {
      triggerFinishReview(doc)
      results = parseResultRows(doc)
    }

    applyInputHighlights(doc, results)

    const total = results.length || doc.querySelectorAll('.blank-input').length
    const correct = results.filter((r) => r.isCorrect).length

    return {
      correct,
      total,
      score: total ? Math.round((correct / total) * 10) / 10 : 0,
      allAnswers: allAnswersFromResults(results),
      wrongAnswers: wrongAnswersFromResults(results),
    }
  } catch {
    return null
  }
}

function allAnswersFromResults(results) {
  const all = {}
  results.forEach((r) => {
    all[`q${r.num}`] = { user_ans: r.userAns, correct_ans: r.correctAns }
  })
  return all
}

function wrongAnswersFromResults(results) {
  const wrong = {}
  results
    .filter((r) => !r.isCorrect)
    .forEach((r) => {
      wrong[`q${r.num}`] = { user_ans: r.userAns, correct_ans: r.correctAns }
    })
  return wrong
}

export function collectAllAnswers(iframe) {
  try {
    const doc = iframe.contentDocument
    if (!doc) return {}
    injectListeningStyles(iframe)
    triggerFinishReview(doc)
    let results = parseResultRows(doc)
    if (!results.length) {
      triggerFinishReview(doc)
      results = parseResultRows(doc)
    }
    return allAnswersFromResults(results)
  } catch {
    return {}
  }
}

export function collectWrongAnswers(iframe) {
  try {
    const doc = iframe.contentDocument
    if (!doc) return {}
    injectListeningStyles(iframe)
    triggerFinishReview(doc)
    const results = parseResultRows(doc)
    return wrongAnswersFromResults(results)
  } catch {
    return {}
  }
}
