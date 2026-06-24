import { defineStore } from 'pinia'
import { ref } from 'vue'
import { fetchUserProfile, patchUserProfile } from '@/api/user'
import { useAuthStore } from './auth'
import { roundIeltsBand } from '@/utils/ieltsScore'

export const useUserStore = defineStore('user', () => {
  const profile = ref(null)
  const loading = ref(false)

  async function refresh() {
    const auth = useAuthStore()
    if (!auth.token) return null
    loading.value = true
    try {
      const data = await fetchUserProfile()
      profile.value = data
      auth.setUser(data)
      return data
    } catch {
      if (auth.user) {
        profile.value = auth.user
        return auth.user
      }
      return null
    } finally {
      loading.value = false
    }
  }

  function applyLocal(profileData) {
    profile.value = profileData
  }

  async function updateExamDate(examDate) {
    const auth = useAuthStore()
    const base = profile.value || auth.user
    if (!base || !examDate) return base

    try {
      const data = await patchUserProfile({ exam_date: examDate })
      profile.value = data
      auth.setUser(data)
      return data
    } catch {
      const next = { ...base, exam_date: examDate }
      profile.value = next
      auth.setUser(next)
      return next
    }
  }

  async function updateTargetScore(targetScore) {
    const auth = useAuthStore()
    const base = profile.value || auth.user
    if (!base || targetScore == null) return base
    const score = roundIeltsBand(targetScore)

    try {
      const data = await patchUserProfile({ target_score: score })
      profile.value = data
      auth.setUser(data)
      return data
    } catch {
      const next = { ...base, target_score: score }
      profile.value = next
      auth.setUser(next)
      return next
    }
  }

  async function applyChatMeta({ exam_date, target_score }) {
    if (exam_date) await updateExamDate(exam_date)
    if (target_score != null) await updateTargetScore(target_score)
  }

  /** 批改完成后更新四科分与收件箱（后端不可用时本地联动） */
  function recordGrade(module, score, { title, meta, icon }) {
    const auth = useAuthStore()
    const base = profile.value || auth.user
    if (!base) return

    const icons = { listening: '🎧', reading: '📖', speaking: '🎤', writing: '📝' }
    const skillScores = { ...base.skill_scores, [module]: roundIeltsBand(score) }
    const vals = Object.values(skillScores)
    const overall = roundIeltsBand(vals.reduce((a, b) => a + b, 0) / vals.length)

    const next = {
      ...base,
      overall_score: overall,
      skill_scores: skillScores,
      inbox: [
        {
          id: `inbox-${Date.now()}`,
          icon: icon || icons[module] || '✨',
          module,
          title,
          meta,
          time: '刚刚',
        },
        ...(base.inbox || []),
      ].slice(0, 20),
    }
    profile.value = next
    auth.setUser(next)
    return next
  }

  async function clearExamDate() {
    const auth = useAuthStore()
    const base = profile.value || auth.user
    if (!base) return null
    const t = new Date()
    const fallback = new Date(t.getFullYear(), t.getMonth(), t.getDate() + 21)
    const iso = fallback.toISOString().slice(0, 10)
    return updateExamDate(iso)
  }

  return {
    profile,
    loading,
    refresh,
    applyLocal,
    recordGrade,
    updateExamDate,
    updateTargetScore,
    applyChatMeta,
    clearExamDate,
  }
})
