const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

let unauthorizedHandler = null

export function setUnauthorizedHandler(handler) {
  unauthorizedHandler = handler
}

export function getToken() {
  return localStorage.getItem('ielts_token') || ''
}

export async function apiFetch(path, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  }
  const token = getToken()
  if (token) headers.Authorization = `Bearer ${token}`

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers })
  if (res.status === 401) {
    unauthorizedHandler?.()
    const err = new Error('会话已失效，请重新登录')
    err.status = 401
    throw err
  }
  if (!res.ok) {
    let message = `HTTP ${res.status}`
    try {
      const body = await res.json()
      if (body?.detail) message = typeof body.detail === 'string' ? body.detail : message
    } catch {
    }
    const err = new Error(message)
    err.status = res.status
    throw err
  }
  return res.json()
}
