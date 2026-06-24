import { apiFetch } from './client'

const MOCK_USER = {
  username: 'admin',
  overall_score: 6.0,
  target_score: 7.0,
  exam_date: '2026-06-25',
  skill_scores: { listening: 6.0, reading: 6.0, speaking: 6.0, writing: 6.0 },
  inbox: [
    {
      id: 'welcome',
      icon: '✨',
      module: 'system',
      title: '欢迎加入雅思智能备考助手',
      meta: '目标 7.0 · 四科均衡起步',
      time: '刚刚',
    },
  ],
}

export async function loginRequest(username, password) {
  try {
    return await apiFetch('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    })
  } catch {
    if (username === 'admin' && password === '123456') {
      return {
        token: `mock-${Date.now()}`,
        user: MOCK_USER,
        source: 'mock',
      }
    }
    throw new Error('login failed')
  }
}
