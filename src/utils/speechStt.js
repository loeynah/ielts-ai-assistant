/** 浏览器实时语音转写（Web Speech API）— 支持长段连续识别 */

export function isSpeechRecognitionSupported() {
  return !!(window.SpeechRecognition || window.webkitSpeechRecognition)
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
      /* onend 会负责重启；静默处理 no-speech / network 等 */
    }

    rec.onend = () => {
      if (listening) {
        window.setTimeout(() => {
          if (!listening) return
          try {
            rec.start()
          } catch {
            if (listening) {
              recognition = buildRecognition()
              try {
                recognition.start()
              } catch {
                /* ignore */
              }
            }
          }
        }, 120)
        return
      }

      if (stopping) {
        appendFinal(interimText)
        interimText = ''
        finishStop(getCombinedText())
      }
    }

    return rec
  }

  function finishStop(text) {
    if (stopTimer) {
      clearTimeout(stopTimer)
      stopTimer = null
    }
    stopping = false
    if (stopCallback) {
      stopCallback(text)
      stopCallback = null
    }
  }

  return {
    start() {
      if (listening) return
      finalText = ''
      interimText = ''
      listening = true
      stopping = false
      recognition = buildRecognition()
      try {
        recognition.start()
      } catch {
        listening = false
        recognition = null
      }
    },

    stop() {
      const textNow = getCombinedText()
      if (!listening && !stopping) return Promise.resolve(textNow)

      return new Promise((resolve) => {
        if (stopping && stopCallback) {
          const prev = stopCallback
          stopCallback = (text) => {
            prev(text)
            resolve(text)
          }
          return
        }

        stopping = true
        listening = false
        stopCallback = resolve

        try {
          recognition?.stop()
        } catch {
          finishStop(getCombinedText())
          return
        }

        stopTimer = window.setTimeout(() => {
          if (stopCallback) finishStop(getCombinedText())
        }, 1200)
      })
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
