import { fetchModuleHistory } from '@/api/history'

function toChartRecord(item) {
  return {
    id: item.id,
    timestamp: item.timestamp,
    exam_id: item.exam_id,
    exam_title: item.exam_title,
    mode: item.mode,
    overall_score: item.overall_score,
    sub_scores: item.sub_scores || {},
    rounds: item.rounds,
    audio_count: item.audio_count,
  }
}

/** 从后端拉取口语练习历史（走势图数据源） */
export async function loadSpeakingHistory() {
  try {
    const list = await fetchModuleHistory('speaking')
    return (list || []).map(toChartRecord)
  } catch {
    return []
  }
}
