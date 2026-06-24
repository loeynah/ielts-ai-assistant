const STORAGE_KEY = 'ielts_speaking_history'

export function loadSpeakingHistory() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
  } catch {
    return []
  }
}

export function saveSpeakingRecord(record) {
  const list = loadSpeakingHistory()
  list.unshift({
    id: `sp-${Date.now()}`,
    timestamp: new Date().toISOString(),
    ...record,
  })
  localStorage.setItem(STORAGE_KEY, JSON.stringify(list.slice(0, 30)))
  return list
}

