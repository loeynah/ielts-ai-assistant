let currentUtterance = null

function pickEnglishVoice(lang = 'en-GB') {
  const voices = speechSynthesis.getVoices()
  return (
    voices.find((v) => v.lang === lang) ||
    voices.find((v) => v.lang.startsWith('en-GB')) ||
    voices.find((v) => v.lang.startsWith('en-US')) ||
    voices.find((v) => v.lang.startsWith('en'))
  )
}

export function speakText(text, { rate = 0.92, lang = 'en-GB', onEnd } = {}) {
  if (!window.speechSynthesis) {
    console.warn('浏览器不支持 Web Speech API')
    return false
  }
  stopSpeaking()
  const utter = new SpeechSynthesisUtterance(text)
  utter.lang = lang
  utter.rate = rate
  const voice = pickEnglishVoice(lang)
  if (voice) utter.voice = voice
  utter.onend = () => {
    currentUtterance = null
    onEnd?.()
  }
  utter.onerror = () => {
    currentUtterance = null
    onEnd?.()
  }
  currentUtterance = utter
  speechSynthesis.speak(utter)
  return true
}

export function stopSpeaking() {
  if (window.speechSynthesis) speechSynthesis.cancel()
  currentUtterance = null
}

export function isSpeaking() {
  return window.speechSynthesis?.speaking ?? false
}

export function preloadVoices() {
  if (!window.speechSynthesis) return
  speechSynthesis.getVoices()
  speechSynthesis.onvoiceschanged = () => speechSynthesis.getVoices()
}
