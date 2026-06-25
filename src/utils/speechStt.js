export function isSpeechRecognitionSupported() {
  return !!(window.SpeechRecognition || window.webkitSpeechRecognition)
}

/** 上一段 STT 完全 stop 后再允许下一段 start（Part1 多题连续录音） */
let pendingStop = Promise.resolve()

export function waitForSttIdle() {
  return pendingStop
}

export function createLiveTranscriber(lang = 'en-US') {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition
  if (!SR) return null

  let finalText = ''
  let interimText = ''
  let listening = false
  let stopping = false
  let recognition = null
  let stopCallback = null
  let stopTimer = null
  let restartTimer = null

  function getCombinedText() {
    const base = finalText.trim()
    const interim = interimText.trim()
    if (!interim) return base
    return base ? `${base} ${interim}` : interim
  }

  function appendFinal(text) {
    const piece = String(text || '').trim()
    if (!piece) return
    finalText = finalText ? `${finalText.trimEnd()} ${piece}` : piece
  }

  function clearRestartTimer() {
    if (restartTimer) {
      clearTimeout(restartTimer)
      restartTimer = null
    }
  }

  function finishStop(text) {
    clearRestartTimer()
    if (stopTimer) {
      clearTimeout(stopTimer)
      stopTimer = null
    }
    stopping = false
    listening = false
    recognition = null
    const cb = stopCallback
    stopCallback = null
    if (cb) cb(text)
  }

  function scheduleRestart(rec) {
    clearRestartTimer()
    restartTimer = window.setTimeout(() => {
      restartTimer = null
      if (!listening || stopping) return
      try {
        rec.start()
      } catch {
        if (!listening || stopping) return
        try {
          recognition = buildRecognition()
          recognition.start()
        } catch {
          listening = false
          recognition = null
        }
      }
    }, 200)
  }

  function buildRecognition() {
    const rec = new SR()
    rec.lang = lang
    rec.interimResults = true
    rec.continuous = true
    rec.maxAlternatives = 1

    rec.onresult = (event) => {
      let interim = ''
      for (let i = event.resultIndex; i < event.results.length; i += 1) {
        const result = event.results[i]
        const piece = result[0]?.transcript || ''
        if (result.isFinal) appendFinal(piece)
        else interim += piece
      }
      interimText = interim
    }

    rec.onerror = () => {
      /* onend 负责恢复或结束 */
    }

    rec.onend = () => {
      if (stopping) {
        appendFinal(interimText)
        interimText = ''
        finishStop(getCombinedText())
        return
      }
      if (listening) scheduleRestart(rec)
    }

    return rec
  }

  return {
    /** 须在用户点击回调链中同步调用，不可在其前 await */
    start() {
      if (listening) return true

      finalText = ''
      interimText = ''
      listening = true
      stopping = false
      clearRestartTimer()
      recognition = buildRecognition()
      try {
        recognition.start()
        return true
      } catch {
        listening = false
        recognition = null
        return false
      }
    },

    stop() {
      const textNow = getCombinedText()
      if (!listening && !stopping) {
        return Promise.resolve(textNow)
      }

      const stopPromise = new Promise((resolve) => {
        if (stopping) {
          const prev = stopCallback
          stopCallback = (text) => {
            if (prev) prev(text)
            resolve(text)
          }
          return
        }

        stopping = true
        listening = false
        clearRestartTimer()

        const rec = recognition
        stopCallback = resolve

        if (!rec) {
          finishStop(getCombinedText())
          return
        }

        try {
          rec.stop()
        } catch {
          finishStop(getCombinedText())
          return
        }

        stopTimer = window.setTimeout(() => {
          if (stopCallback) finishStop(getCombinedText())
        }, 2000)
      })

      pendingStop = stopPromise.finally(() => {
        pendingStop = Promise.resolve()
      })
      return stopPromise
    },

    getText() {
      return getCombinedText()
    },
  }
}

export function hasValidTranscript(text, minChars = 3) {
  const t = String(text || '').trim()
  return t.length >= minChars && t !== '—'
}
